from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Article
from account.views import get_common_context

def articles(request):
    articles_list = Article.objects.filter(is_published=True)
    
    # جستجو
    search = request.GET.get("q")
    if search:
        articles_list = articles_list.filter(title__icontains=search)
    
    # پاگینیشن
    paginator = Paginator(articles_list, 9)  # 9 مقاله در هر صفحه
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    common_context = get_common_context(request)
    common_context.update({
        "articles": articles,
        "search_query": search,
        "page_title": "وبلاگ",
        "meta_description": "آخرین مقالات و اخبار دنیای تکنولوژی",
    })
    context = common_context
    
    return render(request, "articles/articles.html", context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # مقالات مرتبط
    related_articles = Article.objects.filter(is_published=True).exclude(id=article.id)[:3]
    
    common_context = get_common_context(request)
    common_context.update({
        "article": article,
        "related_articles": related_articles,
        "page_title": article.meta_title or article.title,
        "meta_description": article.meta_description or article.short_description or article.title,
        "meta_keywords": article.meta_keywords,
    })
    context = common_context
    return render(request, "articles/article_detail.html", context)



