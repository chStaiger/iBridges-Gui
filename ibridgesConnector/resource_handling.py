from irodsConnector.manager import IrodsConnector
import utils

context = utils.context.Context()
ic = IrodsConnector()

def is_resource_writeable(resc_name: str) -> dict:            
    """
    Verify if default resource is available to write data to
    """
    if resc_name == '':
        return {'successful': False, 'reason': 'Resource name is empty.'}
    resource_info = [(name, status, free_space, context) 
                     for (name, status, free_space, context) in ic.root_resources
                     if name == resc_name]
    # check if irods_default_resource in parent_resources
    if resource_info == []:
        return {'successful': False, 'reason': f'{resc_name} not found or not root resource.'}
    _, status, free_space, resource_context = resource_info[0]
    
    # check status
    if status and status.lower() == 'down':
        return {'successful': False, 'reason': f'{resc_name} is down.'}
    
    # check resource context
    if resource_context is not None:
        write_val = [kvp.split("=")[1] for kvp in resource_context.split(';') if 'write' in kvp]
        if write_val != [] and float(write_val[0] == 0.0):
            return {'successful': False, 'reason': f'{resc_name}: forbidden to write.'}

    # ibridges config: check if free_space nees to be checked
    if context.ibridges_configuration.config.get('check_free_space', True):
        if int(free_space) <= 0:
            return {'successful': False, 'reason': f'{resc_name}: No space left on resource.'}

    return {'successful': True}

def verify_writeable_default_resource() -> dict:
    return is_resource_writeable(ic.default_resc)

def writeable_resources() -> tuple:
    """Discover all writable root resources available in the current
    resources.  A value of 0 indicates no free space annotated.

    Returns
    -------
    list
        Discovered names of writable root resources: (names,
        free_space).

    """
    root_resc_names = [(name, free_space) for (name, _, free_space, _) in ic.root_resources]
    writeable_resources = [(name, free_space) for (name, free_space) in root_resc_names 
                           if is_resource_writeable(name)["successful"] == True]
    return writeable_resources

def resource_space(resc_name: str) -> int:
    """Find the available space left on a resource in bytes.

    Parameters
    ----------
    resc_name : str
        Name of an iRODS resource.

    Returns
    -------
    int
        Number of bytes in `resc_name`.

    Throws: ResourceDoesNotExist if resource not known
            FreeSpaceNotSet if 'free_space' not set

    """
    space = ic.resources(update = True)[resc_name]['free_space']
    if space == -1:
        message = f'RESOURCE ERROR: {resc_name}  does not exist.'
        logging.error(message, resc_name, exc_info=True)
        return {'successful': False, 'reason': message}
    if space == 0:
        message = f'RESOURCE ERROR: Resource "free_space" is not set for {resc_name}.'
        logging.error(message, resc_name, exc_info=True)
        return {'successful': False, 'reason': message}
    # For convenience, free_space is stored multiplied by MULTIPLIER.
    return int(space / kw.MULTIPLIER)
