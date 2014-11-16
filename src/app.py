import os

import api

if __name__ == "__main__":
    api.app.run(host="0.0.0.0", debug=(int(os.environ.get('DEBUG')) != 0))
