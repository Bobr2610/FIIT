from rest_framework import viewsets, permissions
from api.models import Account, Portfolio, Operation, Currency, CurrencyHistory, Rate
from .serializers import (
    UserSerializer, AccountSerializer, PortfolioSerializer,
    OperationSerializer, CurrencySerializer, CurrencyHistorySerializer,
    RateSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    Конечная точка API для просмотра и редактирования информации пользователей.

    Методы:
    
    - `GET`: Получение списка пользователей или информации о конкретном пользователе
    - `POST`: Создание нового пользователя
    - `PUT/PATCH`: Обновление информации пользователя
    - `DELETE`: Удаление пользователя

    Требует аутентификации.
    """
    queryset = Account.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ModelViewSet):
    """
    Конечная точка API для управления аккаунтами пользователей.

    Расширяет функционал стандартной модели пользователя,
    добавляя возможность управления дополнительными полями аккаунта.

    Методы:
    
    - `GET`: Получение списка аккаунтов или информации о конкретном аккаунте
    - `POST`: Создание нового аккаунта
    - `PUT/PATCH`: Обновление информации аккаунта
    - `DELETE`: Удаление аккаунта

    Требует аутентификации.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

class PortfolioViewSet(viewsets.ModelViewSet):
    """
    Конечная точка API для управления портфелями пользователей.

    Позволяет пользователям управлять своими инвестиционными портфелями.
    Каждый пользователь видит только свои портфели.

    Методы:
    
    - `GET`: Получение списка портфелей пользователя или информации о конкретном портфеле
    - `POST`: Создание нового портфеля
    - `PUT/PATCH`: Обновление информации портфеля
    - `DELETE`: Удаление портфеля

    Требует аутентификации.
    """
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(account=self.request.user)

class OperationViewSet(viewsets.ModelViewSet):
    """
    Конечная точка API для управления операциями в портфеле.

    Позволяет пользователям управлять операциями покупки и продажи в своих портфелях.
    Пользователи видят только операции в своих портфелях.

    Методы:
    
    - `GET`: Получение списка операций или информации о конкретной операции
    - `POST`: Создание новой операции (покупка/продажа)
    - `PUT/PATCH`: Обновление информации об операции
    - `DELETE`: Удаление операции

    Требует аутентификации.
    """
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Operation.objects.filter(portfolio__account=self.request.user)

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Конечная точка API для просмотра информации о валютах.

    Предоставляет доступ только для чтения к информации о доступных валютах.
    Нельзя создавать, изменять или удалять валюты через API.

    Методы:
    
    - `GET`: Получение списка валют или информации о конкретной валюте

    Требует аутентификации.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]

class CurrencyHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Конечная точка API для просмотра истории курсов валют.

    Предоставляет доступ только для чтения к историческим данным о курсах валют.
    Нельзя создавать, изменять или удалять исторические данные через API.

    Методы:
    
    - `GET`: Получение истории курсов для конкретной валюты

    Требует аутентификации.
    """
    queryset = CurrencyHistory.objects.all()
    serializer_class = CurrencyHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

class RateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Конечная точка API для просмотра текущих курсов валют.

    Предоставляет доступ только для чтения к текущим курсам валют.
    Нельзя создавать, изменять или удалять курсы через API.

    Методы:
    
    - `GET`: Получение текущих курсов валют

    Требует аутентификации.
    """
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [permissions.IsAuthenticated]