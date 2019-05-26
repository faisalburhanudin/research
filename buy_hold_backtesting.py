from datetime import datetime

import backtrader as bt


class BuyAndHold(bt.Strategy):

    def __init__(self):
        self.data = self.datas[0]
        self.dataclose = self.datas[0].close

        self.bar_executed = None
        self.order = None

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

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (
            trade.pnl, trade.pnlcomm
        ))

    def next(self):
        # Check if an order is pending .. if yes, we cannot send a 2nd one
        if self.order:
            return

        # if change month add cash
        if self.data.datetime.date(0).month > self.data.datetime.date(-1).month:
            # buy stock
            # self.log('BUY!!, %.2f' % self.dataclose[0])

            size = 1_000_000 // self.dataclose[0]
            self.order = self.buy(size=size)
            self.broker.add_cash(1_000_000)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(1_000_000)
    cerebro.broker.setcommission(0.19)

    cerebro.addstrategy(BuyAndHold)

    data = bt.feeds.YahooFinanceData(
        dataname='AAPL',
        fromdate=datetime(2010, 1, 1),
        todate=datetime(2018, 12, 31),
        reverse=False
    )

    cerebro.adddata(data)
    cerebro.run()
    cerebro.plot()
