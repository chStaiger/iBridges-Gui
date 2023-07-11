from irodsConnector.session import Session
import utils
import os
import irods

context = utils.context.Context()
def authenticate(password):
    cached_password = get_cached_password()

    # if password equals cached password --> login with irods env file only
    if cached_password == password:
        sess = Session()
        result = sess.connect()
    # if password differs from cached password --> login with env + password
    else:
        sess = Session(password=password)
        result = sess.connect()
    return result

def get_cached_password() -> str:
    """Scrape the cached password from the iRODS authentication file,
    if it exists.

    Returns
    -------
    str
        Cached password or null string.

    """
    irods_auth_file = os.environ.get(
        'IRODS_AUTHENTICATION_FILE', None)
    if irods_auth_file is None:
        irods_auth_file = context.irods_env_file.path.parent.joinpath(".irodsA")
    if utils.path.LocalPath(irods_auth_file).exists():
        with open(irods_auth_file, encoding='utf-8') as authfd:
            return irods.password_obfuscation.decode(authfd.read())
    return ''

