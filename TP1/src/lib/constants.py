# Status codes
STATUS_OK = 0
ERR_FILE_TOO_BIG = 1

# Sizes as bytes
CHUNK_SIZE = 256
PACKAGE_SIZE = 2
ACK_SIZE = 2
HEADER_SIZE = PACKAGE_SIZE + ACK_SIZE
CLIENT_METHOD_SIZE = 2
FILE_SIZE = 8
STATUS_CODE_SIZE = 2

# Time outs
TIMEOUT = 5 # RANDOM, PERO PONER ALGUNA JUSTIFICACION EN EL INFORME
MAX_TIMEOUTS = 3

# Client methods
UPLOAD = 0
DOWNLOAD = 1

# Opening file modes
READ_MODE = "rb"
WRITE_MODE = "wb"

# Files paths
CLIENT_FILE_PATH = "lib/files/client-files/"
SERVER_FILE_PATH = "lib/files/server-files/"
