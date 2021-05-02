from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def varified_user(request, account_requested):
    """ checks if the user requesting edits is the owner of the post """
    requester = str(request.user.id)
    if requester == str(account_requested):
        return True


def paginate(request, post_list):
    """ set page if specific page is requested """
    page = request.GET.get('page', 1)

    """ split posts into  sets of 10"""
    paginator = Paginator(post_list, 10)

    """ set which posts to display """
    try:
        """ set page requested if request is specific """
        posts = paginator.page(page)
    except PageNotAnInteger:
        """ set page 1 if request is not specific """
        posts = paginator.page(1)
    except EmptyPage:
        """  display final posts if empty page is requested """
        posts = paginator.page(paginator.num_pages)
    return posts


def users_liked_posts(request):
    """ gets a list of liked posts if the user is logged in, allowing the front end to mark posts as liked/unliked """
    liked_posts = ""
    if request.user.is_authenticated:
        liked_posts = request.user.get_liked_posts()
    return liked_posts
