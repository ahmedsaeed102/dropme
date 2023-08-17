# from datetime import date
# from django.shortcuts import redirect
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from drf_spectacular.utils import extend_schema, OpenApiParameter
# from .models import SpecialOffer, Product
# from .serializers import *
# from .services import (
#     product_list,
#     cart_add_entry,
#     entry_delete,
#     entry_update,
#     product_code_get,
# )


# class SpecialOffersList(generics.ListAPIView):
#     queryset = SpecialOffer.objects.filter(end_date__gte=date.today())
#     serializer_class = OfferSerializer
#     permission_classes = (permissions.IsAuthenticated,)


# class ProductsList(generics.ListAPIView):
#     serializer_class = ProductSerializer
#     permission_classes = (permissions.IsAuthenticated,)

#     def get_queryset(self):
#         filters_serializer = ProductFilterSerializer(data=self.request.query_params)
#         filters_serializer.is_valid(raise_exception=True)

#         products = product_list(filters=filters_serializer.validated_data)

#         return products

#     @extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 name="price_points",
#                 location=OpenApiParameter.QUERY,
#                 description="product price points",
#                 required=False,
#                 type=int,
#             ),
#         ],
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)


# class ProductDetail(generics.RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     permission_classes = (permissions.IsAuthenticated,)


# class UserCart(APIView):
#     serializer_class = CartSerializer
#     permission_classes = (permissions.IsAuthenticated,)

#     def get(self, request):
#         return Response(self.serializer_class(request.user.cart).data)


# class AddToCart(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = EntrySerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         cart_add_entry(request=request, data=serializer.validated_data)

#         return redirect("user_cart")


# class RemoveFromCart(APIView):
#     class InputSerializer(serializers.Serializer):
#         entry_id = serializers.IntegerField()

#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = InputSerializer

#     def delete(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         entry_delete(request=request, entry_id=serializer.validated_data["entry_id"])

#         return Response(status=status.HTTP_204_NO_CONTENT)


# class EditCartEntry(APIView):
#     class InputSerializer(serializers.Serializer):
#         entry_id = serializers.IntegerField()
#         quantity = serializers.IntegerField()

#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = InputSerializer

#     def delete(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         entry_update(request=request, data=serializer.validated_data)

#         return Response("Updated")


# class GetProductCode(APIView):
#     class InputSerializer(serializers.Serializer):
#         product_id = serializers.IntegerField()

#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = InputSerializer

#     def get(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         product_code_get(
#             request=request, product_id=serializer.validated_data["product_id"]
#         )

#         return Response("Success")


# class ShowRelatedProducts(APIView):
#     pass
