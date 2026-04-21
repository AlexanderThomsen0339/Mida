from shared.db_manager import get_sources, get_source

def get_all_sources():
    return get_sources()

def get_single_source(source_id: int):
    return get_source(source_id)