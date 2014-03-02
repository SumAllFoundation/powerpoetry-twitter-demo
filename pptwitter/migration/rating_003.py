def forwards(migrator, model):
    """ Create rating table. """
    model.Rating.create_table()
