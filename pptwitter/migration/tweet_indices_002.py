def forwards(migrator, model):
    """ Remove dead columns. Add missing indices. """
    migrator.db.create_index(model.Tweet, ["created_at"])
    migrator.drop_column(model.Tweet, "json_score")
