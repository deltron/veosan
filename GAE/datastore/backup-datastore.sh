

# get stub bulkloader file
# appcfg.py create_bulkloader_config --filename=bulkloader.yaml --application=s~clikcare-stage --url=http://clikcare-stage.appspot.com/_ah/remote_api


appcfg.py download_data --config_file=bulkloader.yaml --kind=Provider --filename=provider.csv --application=s~clikcare-stage --url=http://clikcare-stage.appspot.com/_ah/remote_api
