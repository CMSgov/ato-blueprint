from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone

from .models import Discussion, Comment, Attachment

def makekwargs(request, prefix=""):
    if hasattr(request, "organization"):
        return { prefix+"organization": request.organization }
    return { }

@login_required
@transaction.atomic
def update_discussion_comment_draft(request):
    # Get the discussion object.
    discussion = get_object_or_404(Discussion, id=request.POST['discussion'], **makekwargs(request))

    # Get the text.
    text = request.POST.get("text", "").rstrip()

    comment = None
    if request.POST.get('draft', '') != '':
        # Update existing draft. It's possible the client-side draft
        # ID migth become stale if another browser submits the same
        # draft.
        try:
            comment = discussion.comments.get(id=request.POST['draft'], user=request.user, draft=True)
        except:
            pass
        else:
            comment.text = text
            comment.save()

    if comment is None:
        # Create a new draft.
        comment = discussion.post_comment(
            request.user, text, "web",
            is_draft=True)

    # Return the comment's id and rendered text for displaying a preview.
    return JsonResponse(comment.render_context_dict(request.user))


@login_required
@transaction.atomic
def submit_discussion_comment(request):
    # Get the discussion object.
    discussion = get_object_or_404(Discussion, id=request.POST['discussion'], **makekwargs(request))
    if not discussion.is_participant(request.user):
        return HttpResponseForbidden()

    # Get the Comment draft.
    try:
        comment = discussion.comments.get(id=request.POST['draft'], user=request.user)
    except:
        return JsonResponse({ "status": "error", "message": "No draft." })

    if not comment.draft:
        return JsonResponse({ "status": "error", "message": "It looks like the comment was already submitted from another browser session." })

    # Publish it.
    comment.publish()

    # Return the comment for display.
    return JsonResponse(comment.render_context_dict(request.user))


@login_required
def edit_discussion_comment(request):
    # get object
    comment = get_object_or_404(Comment, id=request.POST['id'], **makekwargs(request, 'discussion__'))

    # can edit? must still be a participant of the discussion, to
    # prevent editing things that you are no longer able to see
    if not comment.can_edit(request.user):
        return HttpResponseForbidden()

    # record edit history
    comment.push_history('text')

    # edit
    comment.text = request.POST['text']

    # save
    comment.save()

    # return new comment info
    return JsonResponse(comment.render_context_dict(request.user))

@login_required
def delete_discussion_comment(request):
    # get object
    comment = get_object_or_404(Comment, id=request.POST['id'], **makekwargs(request, 'discussion__'))

    # can delete? must still be a participant of the discussion, to
    # prevent editing things that you are no longer able to see
    if not comment.can_delete(request.user):
        return HttpResponseForbidden()

    # mark deleted
    comment.deleted = True
    comment.save()

    # return new comment info
    return JsonResponse({ "status": "ok" })

@login_required
def save_reaction(request):
    # get comment that is being reacted *to*
    comment = get_object_or_404(Comment, id=request.POST['id'], **makekwargs(request, 'discussion__'))

    # can see it?
    if not comment.can_see(request.user):
        return HttpResponseForbidden()

    # get the Comment that *reacts* to it
    comment, is_new = Comment.objects.get_or_create(
        discussion=comment.discussion,
        replies_to=comment,
        user=request.user,
    )

    # record edit history
    comment.push_history('emojis')

    # edit
    comment.emojis = request.POST['emojis']

    # save
    comment.save()

    # return new comment info
    return JsonResponse(comment.render_context_dict(request.user))

@login_required
def poll_for_events(request):
    discussion = get_object_or_404(Discussion, id=request.POST['id'])
    if not discussion.is_participant(request.user):
        raise Http404()
    return JsonResponse(discussion.render_context_dict(
        request.user,
        request.POST.get("comment_since", "0"),
        request.POST.get("event_since", "0")
    ))

@login_required
@transaction.atomic
def create_attachments(request):
    # Get the Discussion.
    discussion = get_object_or_404(Discussion, id=request.POST['discussion'])
    if not discussion.is_participant(request.user):
        return HttpResponseForbidden()

    # Get the Comment draft.
    try:
        comment = discussion.comments.get(id=request.POST['draft'], user=request.user, draft=True)
    except:
        return JsonResponse({ "status": "error", "message": "No draft." })

    # The user is uploading one or more files.
    ret = { }
    for fn in request.FILES:
        attachment = Attachment.objects.create(
            comment=comment,
            user=request.user,
            file=request.FILES[fn]
        )

        # Get the dbstorage.models.StoredFile instance which holds
        # an auto-detected mime type. Use that to return whether
        # the attachment is an image or not.
        from dbstorage.models import StoredFile
        sf = StoredFile.objects.get(path=attachment.file.name)
        is_image = sf.mime_type and sf.mime_type.startswith("image/")

        ret[fn] = {
            "id": attachment.id,
            "original_fn": request.FILES[fn].name,
            "is_image": is_image,
        }

    # Return a mapping from file field names in the upload to Attachment infos.
    return JsonResponse(ret)

def download_attachment(request, attachment_id):
    try:
        attachment = get_object_or_404(Attachment, id=attachment_id)
    except ValueError:
        raise Http404()
    if not attachment.comment.discussion.is_participant(request.user):
        return HttpResponseForbidden()

    from dbstorage.views import get_file_content_view
    return get_file_content_view(request, attachment.file.name)
    