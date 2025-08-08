from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import MySet, MySetExercise, MySetExerciseSet
from .serializers import MySetSerializer


@extend_schema_view(
    list=extend_schema(
        summary="マイセット一覧取得",
        description="ログインユーザーのマイセット一覧を取得します。",
        tags=["マイセット"]
    ),
    create=extend_schema(
        summary="マイセット作成",
        description="新しいマイセットを作成します。種目とセット情報も一括で作成できます。",
        tags=["マイセット"]
    ),
    retrieve=extend_schema(
        summary="マイセット詳細取得",
        description="指定したIDのマイセットの詳細を取得します。",
        tags=["マイセット"]
    ),
    update=extend_schema(
        summary="マイセット更新",
        description="指定したIDのマイセットを更新します。種目とセット情報も一括で更新できます。",
        tags=["マイセット"]
    ),
    partial_update=extend_schema(
        summary="マイセット部分更新",
        description="指定したIDのマイセットを部分的に更新します。",
        tags=["マイセット"]
    ),
    destroy=extend_schema(
        summary="マイセット削除",
        description="指定したIDのマイセットを削除します。関連する種目とセット情報も削除されます。",
        tags=["マイセット"]
    ),
)
class MySetViewSet(viewsets.ModelViewSet):
    """
    マイセットのCRUD API

    マイセットの作成、取得、更新、削除を行います。
    すべての操作はログインユーザーのデータのみを対象とします。
    """
    serializer_class = MySetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ログインユーザーのマイセットのみ取得（関連データも含む）"""
        return MySet.objects.filter(
            user_id=self.request.user
        ).prefetch_related(
            Prefetch(
                'exercises',
                queryset=MySetExercise.objects.order_by('order').prefetch_related(
                    Prefetch(
                        'sets',
                        queryset=MySetExerciseSet.objects.order_by('order')
                    )
                )
            )
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """マイセットを作成"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ユーザーが同じ名前のマイセットを持っていないかチェック
        if MySet.objects.filter(
            user_id=request.user,
            name=serializer.validated_data['name']
        ).exists():
            return Response(
                {"name": ["同じ名前のマイセットが既に存在します。"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        """マイセットを更新"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 名前が変更される場合、同じ名前のマイセットが他に存在しないかチェック
        new_name = serializer.validated_data.get('name')
        if new_name and new_name != instance.name:
            if MySet.objects.filter(
                user_id=request.user,
                name=new_name
            ).exclude(id=instance.id).exists():
                return Response(
                    {"name": ["同じ名前のマイセットが既に存在します。"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # prefetchされたキャッシュをクリア
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """マイセットを削除"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        """
        オブジェクトを取得（ユーザーのアクセス権限をチェック）
        ログインユーザーのマイセットのみアクセス可能
        """
        obj = super().get_object()
        if obj.user_id != self.request.user:
            self.permission_denied(
                self.request,
                message="このマイセットにはアクセスできません。"
            )
        return obj
