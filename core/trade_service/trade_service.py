import logging
import sys
from core.trade_service.traders.MA_Trader import MA_Trader
from core.trade_service.traders.baselines import UpperLower_trader
import argparse

logging.basicConfig(filename='trade_service.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol",
                        default="BTCUSDT",
                        help="Crypto symbols. Default: 'BTCUSDT'",
                        nargs="+")
    parser.add_argument("--model",
                        default="MATrader",
                        help="Model to run",
                        type=str)
    parser.add_argument("--mode",
                        default="test",
                        help="Mode to run the trader. [PROD test sim]",
                        type=str)
    parser.add_argument("--interval",
                        default="1h",
                        help="Interval of time to refresh",
                        type=str)
    parser.add_argument("--on_investment",
                        default=False,
                        action="store_true",
                        help="There is a current investment with that symbol")
    parser.add_argument("--percentage_trade",
                        default=1.,
                        help="Percentage of money to invest",
                        type=float)
    parser.add_argument("--period_short",
                        default=14,
                        help="Short period for Moving Avg",
                        type=int)
    parser.add_argument("--period_long",
                        default=25,
                        help="Long period for Moving Avg",
                        type=int)
    parser.add_argument("--panic",
                        default=-0.03,
                        help="Maximum tolerance to sell",
                        type=int)
    args = parser.parse_args()

    logging.info('Start TRADER SERVICE')

    MODELS = {
        "baseline": UpperLower_trader,
        "MATrader": MA_Trader
    }

    if args.model not in MODELS:
        logging.error("The selected model is not present")
        sys.exit(1)

    model = MODELS[args.model](mode=args.mode,
                               symbol=args.symbol,
                               interval_source=args.interval,
                               interval_group=args.interval,
                               on_investment=args.on_investment,
                               period_short=args.period_short,
                               period_long=args.period_long,
                               panic=args.panic
                               )

    logging.info('---------PARAMS---------' + str(model.get_params()))
    model.evaluate(percentage_trade=args.percentage_trade)
