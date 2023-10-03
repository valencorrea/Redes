# Status codes
STATUS_OK = 0
ERR_FILE_TOO_BIG = 1
ERR_FILE_NOT_FOUND = 2

# Sizes as bytes
CHUNK_SIZE = 256
ID_SIZE = 2
ACK_SIZE = 2
HEADER_SIZE = ID_SIZE + ACK_SIZE
CLIENT_METHOD_SIZE = 2
FILE_SIZE = 8
STATUS_CODE_SIZE = 2

# Timeouts
TIMEOUT = 0.1 # RANDOM, PERO PONER ALGUNA JUSTIFICACION EN EL INFORME
MAX_TIMEOUTS = 3
MAX_WINDOW_SIZE = 5

# Client methods
UPLOAD = 0
DOWNLOAD = 1

# Opening file modes
READ_MODE = "rb"
WRITE_MODE = "wb"

# Files paths
CLIENT_FILE_PATH = "lib/files/client-files/"
SERVER_FILE_PATH = "lib/files/server-files/"

# Algorithms
STOP_AND_WAIT = False
