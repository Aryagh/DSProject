def refine_user_info(user_info=None):
    try:
        refined_user_info = {
            'media_count': user_info['media_count'],
            'followers_count': user_info['follower_count'],
            'following_count': user_info['following_count'],
            'user_name': user_info['username'],
            'user_id': user_info['pk'],
            'full_name': user_info['full_name'],
        }
    except KeyError:
        refined_user_info = dict()
    return refined_user_info


def refine_user_list(user_list=None):
    refined_user_list = []
    for user in user_list:
        try:
            refined_user_list.append(
                {
                    'user_id': user['pk'],
                    'user_name': user['username'],
                    'full_name': user['full_name'],
                    'is_private': user['is_private']
                } )
        except KeyError:
            print("There is an error.")
    return refined_user_list


def engagement_calculator(user_posts=None, user_info=None):
    sum_likes = 0
    sum_comments = 0
    followers_count = user_info['followers_count']
    posts_count = len(user_posts['posts'])
    for post in user_posts['posts']:
        try:
            like_count = post['like_count']
        except KeyError:
            like_count = 0
        try:
            comment_count = post['comment_count']
        except KeyError:
            comment_count = 0
        sum_likes += like_count
        sum_comments += comment_count
    sum_engagement = sum_comments + sum_likes
    engagement_rate = 100 * sum_engagement / (followers_count * posts_count)
    engagement_rate = round(engagement_rate, 2)
    engagement_info = {
        'engagement_rate': engagement_rate,
        'likes': int(sum_likes / posts_count),
        'comments': int(sum_comments / posts_count)}
    user_info.update(engagement_info)
    return user_info
