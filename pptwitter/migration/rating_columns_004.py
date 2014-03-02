def forwards(migrator, model):
    """ Rating columns for tweets. """
    migrator.add_column(model.Tweet, model.Tweet.rating, "rating")
    migrator.add_column(model.Tweet, model.Tweet.rate_count, "rate_count")
