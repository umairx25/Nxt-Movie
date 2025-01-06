CREATE EXTERNAL DATA SOURCE MyAzureBlobStorage
WITH ( TYPE = BLOB_STORAGE,
      LOCATION = 'https://xxxxxxxx.blob.core.windows.net/miladcontainer'
      );