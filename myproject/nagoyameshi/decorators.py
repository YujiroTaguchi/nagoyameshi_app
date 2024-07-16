from django.shortcuts import redirect

def subscription_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_subscription_user:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('subscription_required')  # エラーページにリダイレクト
    return _wrapped_view_func