import os
import time
import json
from peewee import *
from .entity import AttachedFile


def prepare_db(dir_path):
    path = os.path.join(dir_path, 'cache.db')
    return SqliteDatabase(path)


def prepare_directory(dir_path):
    os.makedirs(dir_path, exist_ok=True)


dir_path = os.path.expanduser("~/.rucio_jupyterlab")
prepare_directory(dir_path)
db = prepare_db(dir_path)


def get_db():
    db.create_tables([UserConfig, AttachedFilesListCache, FileReplicasCache])
    return DatabaseInstance()


class DatabaseInstance:
    def put_config(self, key, value):
        UserConfig.replace(key=key, value=value).execute()

    def get_config(self, key):
        config = UserConfig.get_or_none(UserConfig.key == key)
        if config:
            return config.value

        return None

    def get_active_instance(self):
        return self.get_config('instance')

    def set_active_instance(self, instance_name):
        self.put_config('instance', instance_name)

    def get_attached_files(self, namespace, did):
        current_time = int(time.time())
        db_attached_files = AttachedFilesListCache.get_or_none(
            (AttachedFilesListCache.namespace == namespace) & (AttachedFilesListCache.did == did) & (AttachedFilesListCache.expiry > current_time))
        if db_attached_files:
            json_attached_files = json.loads(db_attached_files.file_dids)

            attached_files = []
            for json_attached_file in json_attached_files:
                attached_file = AttachedFile(did=json_attached_file.get('did'), size=json_attached_file.get('size'))
                attached_files.append(attached_file)

            return attached_files

        return None

    def set_attached_files(self, namespace, parent_did, attached_files):
        cache_expires = int(time.time()) + (3600)  # an hour TODO change?
        attached_files_dict = [x.__dict__ for x in attached_files]
        file_dids_json = json.dumps(attached_files_dict)
        AttachedFilesListCache.replace(namespace=namespace, did=parent_did,
                                       file_dids=file_dids_json, expiry=cache_expires).execute()

    def get_file_replica(self, namespace, file_did):
        current_time = int(time.time())
        replica_cache = FileReplicasCache.get_or_none((FileReplicasCache.namespace == namespace) & (
            FileReplicasCache.did == file_did) & (FileReplicasCache.expiry > current_time))

        return replica_cache

    def set_file_replica(self, namespace, file_did, pfn, size):
        cache_expires = int(time.time()) + (3600)  # an hour TODO change?
        FileReplicasCache.replace(
            namespace=namespace, did=file_did, pfn=pfn, size=size, expiry=cache_expires).execute()


class UserConfig(Model):
    key = TextField(unique=True)
    value = TextField()

    class Meta:
        database = db


class AttachedFilesListCache(Model):
    namespace = TextField()
    did = TextField()
    file_dids = TextField()
    expiry = DateTimeField()

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'did')


class FileReplicasCache(Model):
    namespace = TextField()
    did = TextField()
    pfn = TextField(null=True)
    size = IntegerField()
    expiry = DateTimeField()

    class Meta:
        database = db
        primary_key = CompositeKey('namespace', 'did')
