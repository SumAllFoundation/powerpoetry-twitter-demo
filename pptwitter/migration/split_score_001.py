def forwards(migrator, model):
    """ Move features to their own columns for indexing. """
    migrator.db.create_index(model.Tweet, ["tweeted_by"])
    migrator.rename_column(model.Tweet, "score", "json_score")
    migrator.add_column(model.Tweet, model.Tweet.score, "score")
    migrator.add_column(model.Tweet, model.Tweet.language, "language")
    migrator.add_column(model.Tweet, model.Tweet.poetic, "poetic")
    migrator.add_column(model.Tweet, model.Tweet.sentiment, "sentiment")

    for tweet in model.Tweet.select():
        tweet.score = sum(tweet.json_score.values()) / 3.0
        tweet.language = tweet.json_score["language"]
        tweet.poetic = tweet.json_score["poetic"]
        tweet.sentiment = tweet.json_score["sentiment"]
        tweet.save()
