from os import name
from time import process_time_ns
from turtle import title
from django.shortcuts import render, redirect

from . import util

import markdown2
import random
import bleach

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        if title.lower() in list(map(str.lower, util.list_entries())):
            return render(request, "encyclopedia/create.html", {
                "title": title,
                "content": content,
                "error": f'An entry named "{title}" already exist.'
            })

        util.save_entry(title, content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/create.html")

def entry(request, title=None):
    if not title:
        title = "NO TITLE!"

    content = util.get_entry(title)

    if not content:

        return render(request, "encyclopedia/entry.html", {
            "entry": title,
            "error": f"No such title: {title}"
        })

    content = markdown2.markdown(content)

    allowed_tags = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre',
    'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'img']

    allowed_attrs = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height']}

    content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)

    return render(request, "encyclopedia/entry.html", {
        "entry": title,
        "content": content
    })

def random_entry(request):
    entries = util.list_entries()
    entry = random.choice(entries)
    return redirect("entry", title=entry)


def search(request, query=None):
    query = request.GET.get("q")
    if not query:
        return redirect("index")

    if query.lower() in list(map(str.lower, util.list_entries())):
        return redirect("entry", title=query)

    results = [entry for entry in util.list_entries() if query.lower() in entry.lower()]

    return render(request, "encyclopedia/search_page.html", {
        "query": query,
        "results": results
    })


def edit(request, title=None):
    if request.method == "POST":
        content = request.POST.get("content").replace('\r\n', '\n')

        util.save_entry(title, content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/edit.html", {
        "entry": title,
        "content": util.get_entry(title)
    })







