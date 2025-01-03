from rest_framework import status
from rest_framework.generics import (
    ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView,
    ListCreateAPIView, DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from car.models import (
    CarCategory, CarBrand, CarModel, Car, OilChange, Consumables, PartCategory,
    Part, CarBody, PartManufacturerCountry, CarDrive
)
from car.permissions import IsCarOwner
from car.serializers import (
    CarCategorySerializer, CarBrandSerializer, CarModelSerializer,
    CarSerializer, OilChangeSerializer, ConsumablesSerializer,
    PartCategorySerializer, PartSerializer, CarListSerializer,
    CarBodySerializer, PartManufacturerCountrySerializer, CarDetailSerializer,
    CarDriveSerializer
)


class EngineListView(APIView):
    def get(self, *args, **kwargs):
        engines = [
            {"engine": data[0], "title": data[1]} for data in Car.engines
        ]
        return Response(engines, status=status.HTTP_200_OK)


class TransmissionListView(APIView):
    def get(self, *args, **kwargs):
        transmissions = [
            {"transmission": data[0], "title": data[1]}
            for data in Car.transmissions
        ]
        return Response(transmissions, status=status.HTTP_200_OK)


class DrivesListView(ListAPIView):
    queryset = CarDrive.objects.all()
    serializer_class = CarDriveSerializer


class CarCategoryListView(ListAPIView):
    queryset = CarCategory.objects.all()
    serializer_class = CarCategorySerializer


class CarBrandListView(ListAPIView):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer
    filterset_fields = ['category',]


class CarModelListView(ListAPIView):
    serializer_class = CarModelSerializer
    filterset_fields = ['brand', 'category']
    queryset = CarModel.objects.all()


class CarBodyListView(ListAPIView):
    serializer_class = CarBodySerializer
    queryset = CarBody.objects.all()


class CarListView(ListAPIView):
    serializer_class = CarListSerializer

    def get_queryset(self):
        return Car.objects.filter(user=self.request.user)


class CarCreateView(CreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CarDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsCarOwner)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CarDetailSerializer
        return CarSerializer

    def get_queryset(self):
        return Car.objects.filter(user=self.request.user)


class OilChangeListCreateView(ListCreateAPIView):
    serializer_class = OilChangeSerializer
    permission_classes = (IsAuthenticated, IsCarOwner)

    def perform_create(self, serializer):
        car_id = self.kwargs['car_id']
        serializer.save(car_id=car_id)

    def get_queryset(self):
        car_id = self.kwargs['car_id']
        return OilChange.objects.filter(car_id=car_id).order_by('change_date')


class OilChangeDeleteView(DestroyAPIView):
    serializer_class = OilChangeSerializer
    permission_classes = (IsAuthenticated, IsCarOwner)

    def get_queryset(self):
        car_id = self.kwargs['car_id']
        return OilChange.objects.filter(car_id=car_id)


class ConsumablesListCreateView(ListCreateAPIView):
    serializer_class = ConsumablesSerializer
    permission_classes = (IsAuthenticated, IsCarOwner)

    def perform_create(self, serializer):
        car_id = self.kwargs['car_id']
        serializer.save(car_id=car_id)

    def get_queryset(self):
        car_id = self.kwargs['car_id']
        return Consumables.objects.filter(car_id=car_id)


class ConsumablesDeleteView(DestroyAPIView):
    serializer_class = OilChangeSerializer
    permission_classes = (IsAuthenticated, IsCarOwner)

    def get_queryset(self):
        car_id = self.kwargs['car_id']
        return Consumables.objects.filter(car_id=car_id)


class PartCategoryListView(ListAPIView):
    serializer_class = PartCategorySerializer
    queryset = PartCategory.objects.all()


class PartListView(ListAPIView):
    serializer_class = PartSerializer
    queryset = Part.objects.all()
    filterset_fields = ('category',)


class CommonPartListView(ListAPIView):
    serializer_class = PartSerializer
    queryset = Part.objects.filter(category__is_common_parts=True)


class PartManufacturerCountryListView(ListAPIView):
    serializer_class = PartManufacturerCountrySerializer
    queryset = PartManufacturerCountry.objects.all()
