from django.db import models
from journal.settings import AUTH_USER_MODEL as User
from django.utils import timezone

# datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')

# Create your models here.


class TwitterUser(models.Model):
    
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    # for checking whether it is coming from original seed tweet lists
    active = models.BooleanField(default=False)
    exception = models.CharField(max_length=595, blank=True, null=True)
    seed = models.BooleanField(default=False)

    # for seeing where it came from (which dataset + which pre_annotation the tweet had)
    hateval = models.BooleanField(default=False)
    offenseval = models.BooleanField(default=False)
    pre_annotation = models.TextField(null=False)

    name = models.CharField(max_length=600)
    screen_name = models.CharField(max_length=600)
    profile_image_url = models.URLField(max_length=1000)
    url = models.URLField(max_length=600, null=True)
    location = models.CharField(max_length=600)
    description = models.TextField()

    nr_tweets = models.IntegerField(default=0, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    friends_count = models.IntegerField(blank=True, null=True)
    statuses_count = models.IntegerField(blank=True, null=True)

    geo_enabled = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)

    follow_back = models.TextField(blank=True, default='')
    follow_back_cnt = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "[{0}] TwitterUser ID: {1}, Username: {2}".format(self.id, self.user_id, self.screen_name)


class Symbol(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=300)
    start_chr = models.IntegerField(blank=True, null=True)
    end_chr = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(default=1, null=True)

    def __str__(self):
        return self.text


class Url(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.URLField(max_length=1000)
    expanded_url = models.URLField(max_length=1000)
    display_url = models.URLField(max_length=1000)
    start_chr = models.IntegerField(blank=True, null=True)
    end_chr = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(default=1, null=True)

    def __str__(self):
        return self.url


class UserMention(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=600)
    screen_name = models.CharField(max_length=600, blank=True, null=True)
    user_mention_id = models.BigIntegerField(blank=True, null=True)
    start_chr = models.IntegerField(blank=True, null=True)
    end_chr = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(default=1, null=True)

    def __str__(self):
        return self.name


class Hashtag(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=600, blank=True, null=True)
    start_chr = models.IntegerField(blank=True, null=True)
    end_chr = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(default=1, null=True)

    def __str__(self):
        return self.text


class Tweet(models.Model):

    id = models.AutoField(primary_key=True)
    tweet_id = models.BigIntegerField(blank=True, null=True)
    user_id = models.ForeignKey(TwitterUser, related_name="twitter_user", on_delete=models.CASCADE, blank=True, null=True)

    # for checking whether it is coming from original seed tweet lists
    active = models.BooleanField(default=False)
    exception = models.CharField(max_length=600, blank=True, null=True)
    seed = models.BooleanField(default=False)
    hateval = models.BooleanField(default=False)
    offenseval = models.BooleanField(default=False)

    avg_conf = models.FloatField(blank=True, null=True)
    offenseval_bucket = models.CharField(max_length=600, blank=True, null=True)
    pre_annotation = models.CharField(max_length=600, blank=True, null=True)

    text = models.TextField()

    in_reply_to_status_id = models.BigIntegerField(blank=True, null=True)
    in_reply_to_user_id = models.BigIntegerField(blank=True, null=True)
    in_reply_to_self = models.BooleanField(default=False)

    created_at = models.DateTimeField(blank=True, null=True)
    lang = models.CharField(max_length=300, blank=True, null=True)
    retweet_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)

    truncated = models.BooleanField(default=False)
    is_quote_status = models.BooleanField(default=False)
    favorited = models.BooleanField(default=False)
    retweeted = models.BooleanField(default=False)
    possibly_sensitive = models.BooleanField(default=False)
    possibly_sensitive_appealable = models.BooleanField(default=False)

    hashtags = models.ManyToManyField(Hashtag)
    user_mentions = models.ManyToManyField(UserMention)
    urls = models.ManyToManyField(Url)
    symbols = models.ManyToManyField(Symbol)

    def __str__(self):
        return "[{0}] Twitter ID: {1}, by Twitter user: {2}".format(self.id, self.tweet_id, self.user_id)

    class Meta:
        db_table = 'thesis_tweets'


class Abuse(models.Model):
    id = models.AutoField(primary_key=True)
    tweet_id = models.ForeignKey(Tweet, related_name="abuse_tweet", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="abuse_user", on_delete=models.CASCADE)
    annotation = models.CharField(max_length=10, default=None, null=True)
    first_created = models.DateTimeField(editable=False, auto_now_add=True)
    first_viewed = models.DateTimeField(null=True, blank=True)
    last_saved = models.DateTimeField(editable=False, auto_now=True)
    annotated_count = models.IntegerField(default=0)

    def __str__(self):
        return "[Abuse] {0}, {1}: {2}".format(self.id, self.user, self.annotation)

    class Meta:
        db_table = 'abuse_annotations'


class Implicit(models.Model):
    id = models.AutoField(primary_key=True)
    tweet_id = models.ForeignKey(Tweet, related_name="implicit_tweet", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="implicit_user", on_delete=models.CASCADE)
    annotation = models.CharField(max_length=10, default=None, null=True)
    first_created = models.DateTimeField(editable=False, auto_now_add=True)
    first_viewed = models.DateTimeField(null=True, blank=True)
    last_saved = models.DateTimeField(editable=False, auto_now=True)
    annotated_count = models.IntegerField(default=0)

    def __str__(self):
        return "[Implicit] {0}, {1}: {2}".format(self.id, self.user, self.annotation)

    class Meta:
        db_table = 'implicit_annotations'
