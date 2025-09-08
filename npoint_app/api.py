from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from django.conf import settings
from django.db.models import F



from .models import JSONData
from .serializers import JSONDataSerializer


class JSONDataViewSet(viewsets.ModelViewSet):
    queryset = JSONData.objects.all()
    serializer_class = JSONDataSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return JSONData.objects.filter(Q(is_public=True) | Q(user=user))
        return JSONData.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='content' )
    def my_jsons(self, request):
        user = request.user
        jsons = JSONData.objects.filter(user=user)
        page = self.paginate_queryset(jsons)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(jsons, many=True)
        return Response(serializer.data)
    
    def content(self, request, pk=None):
        obj = self.get_object()
        # ensure non-owners can only see public docs
        if not obj.is_public and (not request.user.is_authenticated or request.user != obj.user):
            return Response(status=404)
        return Response(obj.json_content)


# class MyViewSet(viewsets.ViewSet):
#     """
#     ViewSet that uses list() with username and slug from URL.
#     """

#     def list(self, request, username=None, slug=None, json_id=None):
        
#         json_model = JSONData.objects.get(json_id=json_id)
#         serializer = JSONDataSerializer(json_model) 
        


#         return Response(serializer.data)
    
class MyViewSet(viewsets.ViewSet):
    """
    GET /api/public/json/<username>/<slug>/<json_id>/
    - Auth (token) required for everyone.
    - Public docs: any authenticated user can read.
    - Private docs: only the owner can read (404 for others).
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]         # token-only auth
    permission_classes = ([permissions.AllowAny] if settings.DEBUG else [permissions.IsAuthenticated])     # reject anonymous with 401

    def list(self, request, username=None, slug=None, json_id=None):
        # Load by id + username; keep slug as a consistency check
        obj = get_object_or_404(
            JSONData.objects.select_related("user"),
            pk=json_id,
            user__username=username,
        )
        if obj.slug != slug:
            raise Http404

        # Access control: public → ok for any authenticated user; private → only owner
        if not obj.is_public and request.user.id != obj.user_id:
            raise Http404  # hide existence

        # Optional: increment access counter
        JSONData.objects.filter(pk=obj.pk).update(access_count=F("access_count") + 1)
        obj.refresh_from_db() 
        ser = JSONDataSerializer(obj)
        return Response(ser.data)