import json
from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from baratheon.utils.logs import logger
import baratheon.settings as settings

from stark.models.product import Product, ProductSchema

import falcon
from gevent import monkey
monkey.patch_all()

from dogpile.cache import make_region
from threading import Thread


''' Cache region for dogpile.cache '''
cache = make_region(
    key_mangler=lambda key: "baratheon:dogpile:" + key
).configure(
    'dogpile.cache.redis',
    arguments={
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
        'redis_expiration_time': 60*60*2,  # 2 hours
        'distributed_lock': True
    },
)


def cache_refresh(session, refresher, *args, **kwargs):
    '''
    Refresh the functions cache data in a new thread. Starts
    refreshing only after the session was committed so all
    database data is available.
    '''
    assert isinstance(session, Session), \
        'Need a session, not a sessionmaker or scoped_session'

    @event.listens_for(session, 'after_commit')
    def do_refresh(session):
        t = Thread(target=refresher, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()


class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'Unsupported response encoding',
                href='http://stark.jualio.com/api/v1/docs.html')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'Unsupported content type',
                    href='')


class JSONTranslator(object):

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes form the request body
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A calid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753, 'Malformed JSON',
                                   'Could not decode the request body. '
                                   'The JSON was incorrect or not encoded '
                                   'as UTF-8')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'])


class ProductEngine(object):

    def __init__(self, db):
        self.db = db

    @cache.cache_on_arguments()
    def get_products(self):
        criteria = self.db.query(Product)
        products = criteria.all()
        logger.debug('found %i products', len(products))
        return products


class ProductsResources:

    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp):
        try:
            products = self.db.get_products()
            serializer = ProductSchema(many=True)
            result = serializer.dump(products).data

        except Exception as e:
            logger.exception(e)

            description = ('Fetch data failed')
            raise falcon.HTTPServiceUnavailable(
                'Service unavailable',
                description,
                30)

        req.context['result'] = result
        resp.status = falcon.HTTP_200


# Configure wsgi server to load baratheon.app
app = falcon.API(middleware=[
    RequireJSON(),
    JSONTranslator()
])

db_user = settings.DATABASE.get('USER', 'postgres')
db_pass = settings.DATABASE.get('PASSWORD', '')
db_server = settings.DATABASE.get('HOST', 'localhost')
db_port = settings.DATABASE.get('PORT', '5432')
db_name = settings.DATABASE.get('NAME', '')
dsn = "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
    db_user,
    db_pass,
    db_server,
    db_port,
    db_name
)

db_engine = create_engine(dsn, echo=True)
db = scoped_session(sessionmaker(bind=db_engine))

product_db = ProductEngine(db)
product_resources = ProductsResources(product_db)

api_version = '/api/' + settings.DEFAULT_API

app.add_route(api_version + '/products', product_resources)
