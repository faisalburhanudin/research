from datetime import datetime

import backtrader as bt


class TestStrategy(bt.Strategy):

    def __init__(self):
        self.dataclose = self.datas[0].close

        # To keep track of pending orders
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.bar_executed = 0

        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=15
        )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY Executed, Price: %.2f, Cost: %.2f, Comm %.2f' % (
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm
                ))
            elif order.issell():
                self.log('SELL Executed, Price: %.2f, Cost: %.2f, Comm: %.2f' % (
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm
                ))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (
            trade.pnl, trade.pnlcomm
        ))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending .. if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check in we are in the market
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY!!, %.2f' % self.dataclose[0])
                self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    cerebro.broker.set_cash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    data = bt.feeds.YahooFinanceCSVData(
        dataname='dataset/orcl-1995-2014.txt',
        fromdate=datetime(2000, 1, 1),
        todate=datetime(2000, 12, 31),
        reverse=False
    )

    cerebro.adddata(data)

    value = cerebro.broker.getvalue()
    print(f'Starting portfolio value: {value}')

    cerebro.run()

    value = cerebro.broker.getvalue()
    print(f'Final portfolio value: {value}')

    cerebro.plot()
