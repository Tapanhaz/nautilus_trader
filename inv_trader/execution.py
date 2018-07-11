#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
# <copyright file="execution.py" company="Invariance Pte">
#  Copyright (C) 2018 Invariance Pte. All rights reserved.
#  The use of this source code is governed by the license as found in the LICENSE.md file.
#  http://www.invariance.com
# </copyright>
# -------------------------------------------------------------------------------------------------

import abc
import datetime
import uuid

from decimal import Decimal
from typing import List
from typing import Dict

from inv_trader.model.enums import Venue, Resolution, QuoteType, OrderSide, OrderType, OrderStatus
from inv_trader.model.objects import Symbol, BarType, Bar
from inv_trader.model.order import Order
from inv_trader.model.events import Event, OrderEvent
from inv_trader.model.events import OrderSubmitted, OrderAccepted, OrderRejected, OrderWorking
from inv_trader.model.events import OrderExpired, OrderModified, OrderCancelled, OrderCancelReject
from inv_trader.strategy import TradeStrategy

StrategyId = str
OrderId = str


class ExecutionClient:
    """
    The abstract base class for all execution clients.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """
        Initializes a new instance of the ExecutionClient class.
        """
        self._registered_strategies = {}  # type: Dict[StrategyId, callable]
        self._order_index = {}            # type: Dict[OrderId, StrategyId]

    def register_strategy(self, strategy: TradeStrategy):
        """
        Register the given strategy with the execution client.
        """
        # Preconditions
        if not isinstance(strategy, TradeStrategy):
            raise TypeError(f"The strategy is not a type of TradeStrategy (was {type(strategy)}).")

        strategy_id = str(strategy)

        if strategy_id in self._registered_strategies.keys():
            raise ValueError("The strategy does not have a unique name and label.")

        self._registered_strategies[strategy_id] = strategy._update_events
        strategy._register_execution_client(self)

    @abc.abstractmethod
    def connect(self):
        """
        Connect to the execution service.
        """
        # Raise exception if not overridden in implementation.
        raise NotImplementedError("Method must be implemented in the execution client.")

    @abc.abstractmethod
    def disconnect(self):
        """
        Disconnect from the execution service.
        """
        # Raise exception if not overridden in implementation.
        raise NotImplementedError("Method must be implemented in the execution client.")

    @abc.abstractmethod
    def submit_order(
            self,
            order: Order,
            strategy_id: StrategyId):
        """
        Send a submit order request to the execution service.
        """
        # Raise exception if not overridden in implementation.
        raise NotImplementedError("Method must be implemented in the execution client.")

    @abc.abstractmethod
    def cancel_order(self, order: Order):
        """
        Send a cancel order request to the execution service.
        """
        # Raise exception if not overridden in implementation.
        raise NotImplementedError("Method must be implemented in the execution client.")

    @abc.abstractmethod
    def modify_order(self, order: Order, new_price: Decimal):
        """
        Send a modify order request to the execution service.
        """
        # Raise exception if not overridden in implementation.
        raise NotImplementedError("Method must be implemented in the execution client.")

    def _register_order(
            self,
            order: Order,
            strategy_id: StrategyId):
        """
        Register the given order with the execution client.

        :param order: The order to register.
        :param strategy_id: The strategy id to register with the order.
        """
        # Preconditions
        if not isinstance(order, Order):
            raise TypeError(f"The order is not a type of Order (was {type(order)}).")

        if order.id in self._order_index.keys():
            raise ValueError(f"The order does not have a unique id.")

        self._order_index[order.id] = strategy_id

    def _on_event(self, event: Event):
        """
        Handle events received from the execution service.
        """
        if not isinstance(event, Event):
            TypeError(f"The event is not of type Event (was {type(event)}).")

        # If event order id contained in order index then send to strategy.
        if isinstance(event, OrderEvent):
            order_id = event.order_id
            if order_id in self._order_index.keys():
                strategy_id = self._order_index[order_id]
                self._registered_strategies[strategy_id](event)
                return
            self._log(f"Execution: Warning given event order id not contained in index {order_id}")

    @staticmethod
    def _log(message: str):
        """
        Log the given message (if no logger then prints).

        :param message: The message to log.
        """
        print(message)


class MockExecClient(ExecutionClient):
    """
    Provides a mock execution client for trading strategies.
    """

    def connect(self):
        """
        Connect to the execution service.
        """
        self._log("MockExecClient connected.")

    def disconnect(self):
        """
        Disconnect from the execution service.
        """
        self._log("MockExecClient disconnected.")

    def submit_order(
            self,
            order: Order,
            strategy_id: StrategyId):
        """
        Send a submit order request to the execution service.
        """
        super()._register_order(order, strategy_id)

        order_submitted = OrderSubmitted(
            order.symbol,
            order.id,
            datetime.datetime.utcnow(),
            uuid.uuid4(),
            datetime.datetime.utcnow())

        order_accepted = OrderAccepted(
            order.symbol,
            order.id,
            datetime.datetime.utcnow(),
            uuid.uuid4(),
            datetime.datetime.utcnow())

        order_working = OrderWorking(
            order.symbol,
            order.id,
            'B' + order.id,
            datetime.datetime.utcnow(),
            uuid.uuid4(),
            datetime.datetime.utcnow())

        super()._on_event(order_submitted)
        super()._on_event(order_accepted)
        super()._on_event(order_working)

    def cancel_order(self, order: Order):
        """
        Send a cancel order request to the execution service.
        """
        order_cancelled = OrderCancelled(
            order.symbol,
            order.id,
            datetime.datetime.utcnow(),
            uuid.uuid4(),
            datetime.datetime.utcnow())

        super()._on_event(order_cancelled)

    def modify_order(self, order: Order, new_price: Decimal):
        """
        Send a modify order request to the execution service.
        """
        order_modified = OrderModified(
            order.symbol,
            order.id,
            'B' + order.id,
            new_price,
            datetime.datetime.utcnow(),
            uuid.uuid4(),
            datetime.datetime.utcnow())

        super()._on_event(order_modified)


class LiveExecClient(ExecutionClient):
    """
    Provides a live execution client for trading strategies.
    """

    def connect(self):
        """
        Connect to the execution service.
        """
        # TODO
        self._log("LiveExecClient connected.")

    def disconnect(self):
        """
        Disconnect from the execution service.
        """
        # TODO
        self._log("Execution client disconnected.")

    def submit_order(
            self,
            order: Order,
            strategy_id: StrategyId):
        """
        Send a submit order request to the execution service.
        """
        super()._register_order(order, strategy_id)
        # TODO

    def cancel_order(self, order: Order):
        """
        Send a cancel order request to the execution service.
        """
        # TODO
        pass

    def modify_order(
            self,
            order: Order,
            new_price: Decimal):
        """
        Send a modify order request to the execution service.
        """
        # TODO
        pass
