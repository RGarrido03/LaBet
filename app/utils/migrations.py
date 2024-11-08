from django.db import connection
from django.db.migrations.loader import MigrationLoader


def get_last_migration(app_name):
    # Initialize the migration loader
    loader = MigrationLoader(connection)
    # Get the migration graph
    graph = loader.graph

    # Filter migrations for the specified app
    app_migrations = [key for key in graph.leaf_nodes() if key[0] == app_name]

    if not app_migrations:
        return None

    # Return the last migration name
    return app_migrations[0][1]
