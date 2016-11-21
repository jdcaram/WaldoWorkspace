# WaldoWorkspace

API Project to retrieve images from S3 and process for EXIF information.

## API Methods

1. /api/1/photos/ 
    * Retrieve all Photos (Paged at 50)
    * To Filter by a Certain EXIF Value - pass as a URL Param
        * key: exif-<EXIF Key Name>
        * value: value as a string
        * example: /api/1/photos/?exif-DateTimeOriginal=2016:03:04%2017:59:38
2. /api/1/photos/{{key}}/
    * Retrieve just 1 photo
    * All the EXIF information will be passed back as well
3. /api/1/exif_items/
    * Retrieve all exif_items
    * Can filter by Photo or Key/Value
         * /api/1/exif_items/?exif_name=ExposureTime&exif_value=(10,%2032000)
         * /api/1/exif_items/?photo={{key}}
4. /api/1/action/
    * API POST Endpoint to Process the Photos or Delete the photos
    * key="action"
    * value can be "retrieve" (which processes the photos) or "delete" which cleans the Database up
    
## Notes

The username and password for the web side is "admin" and "waldoadmin".
There is nothing really implemented for the Web/Browser - just the start.  
The REST API would also require permissions for calling the objects
and processing.  It was easier for testing to leave that off.


        
    
