import json
from pathlib import Path
from logging import config, getLogger

from leauwps.core import main


# log設定の読み込み
current_dir = Path(__file__).parent.resolve()
log_config = Path.joinpath(current_dir, 'leauwps', 'log', 'config.json')
with open(log_config) as f:
    config.dictConfig(json.load(f))

logger = getLogger(__name__)


if __name__ == '__main__':
    logger.info('===== Leauwps started =====')
    main()
    logger.info('===== Leauwps end =====')
