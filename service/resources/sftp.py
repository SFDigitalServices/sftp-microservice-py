""" SFTP module"""
import os
import json
import falcon
import jsend
import pysftp
import sentry_sdk
from pathvalidate import is_valid_filename
from .hooks import validate_access, validate_required_fields

@falcon.before(validate_access)
class SFTP():
    """ SFTP class """
    @falcon.before(validate_required_fields, {'params':['remotepath', 'filename']})
    def on_post(self, req, resp):
        #pylint: disable=too-many-locals
        """on post request
        return either sucessful transfer or error message
        """
        msg_error = "Generic Error"

        sftp_info = self.get_sftp_info(req)

        remote_path = req.params['remotepath']
        file_name = req.params['filename']
        local_dir = os.environ['LOCAL_DIR']
        local_file_path = os.path.join(local_dir, file_name)

        if(not file_name or file_name[0] == '.' or not is_valid_filename(file_name)):
            return self.resp_error("Invalid Filename", resp)

        data = req.bounded_stream.read()
        file = open(local_file_path, "wb+")
        file_written = file.write(data)
        file.close()

        if not isinstance(file_written, int):
            return self.resp_error("Cannot write file", resp)

        local_file_host_path = os.path.join(local_dir, 'host_'+file_name)
        file_host = open(local_file_host_path, "w+")
        file_host_written = file_host.write(sftp_info['HOST-KEY'])
        file_host.close()

        if not file_host_written:
            if file_written:
                try:
                    os.remove(local_file_path)
                #pylint: disable=broad-except
                except Exception as exception:
                    with sentry_sdk.configure_scope() as scope:
                        scope.set_extra('remote_local_exception', str(exception))
            return self.resp_error("Cannot write host file", resp)

        sftp_put = None

        if file_written:
            try:
                sftp_put = self.transfer_file(sftp_info, local_file_path,
                                              remote_path, local_file_host_path)
            #pylint: disable=broad-except
            except Exception as exception:
                msg_error = "Cannot transfer file: "+str(exception)
                return self.resp_error(msg_error, resp)
            finally:
                os.remove(local_file_path)
                os.remove(local_file_host_path)

        if sftp_put:
            msg = {'message': "File transferred successfully"}
            resp.body = json.dumps(jsend.success(msg))
            resp.status = falcon.HTTP_200
            return True

        return self.resp_error(msg_error, resp)

    @staticmethod
    def resp_error(msg, resp):
        """ Sets response error """
        with sentry_sdk.configure_scope() as scope:
            scope.set_extra('message', msg)
            sentry_sdk.capture_message('sftp.resp_error', 'error')
        resp.body = json.dumps(jsend.error(msg))
        resp.status = falcon.HTTP_400

    @staticmethod
    def transfer_file(sftp_info, localpath,
                      remotepath, file_host_path=None, cnopts=None):
        """ Transfer file method """
        sftp_host = sftp_info['HOST']
        sftp_user = sftp_info['USER']
        sftp_password = sftp_info['PASSWORD']

        sftp_put = None

        if not cnopts:
            cnopts = pysftp.CnOpts()
        if file_host_path:
            cnopts.hostkeys.load(file_host_path)

        sftp = pysftp.Connection(sftp_host, cnopts=cnopts,
                                 username=sftp_user, password=sftp_password)

        if sftp:
            sftp.cd()
            sftp.chdir(remotepath)
            sftp_put = sftp.put(localpath, preserve_mtime=True)
            sftp.close()

        return sftp_put

    @staticmethod
    def get_sftp_info(req):
        """ Get SFTP information from request and environment variables
        returns dictory with following keys:
        HOST, USER, PASSWORD, HOST-KEY
        """
        sftp_info = {}
        sftp_info['HOST-KEY'] = os.environ['KNOWN_HOST']

        sftp_bundle = req.get_header('X-SFTP-BUNDLE')
        if(sftp_bundle and sftp_bundle.isalnum()
           and ('BUNDLE_'+sftp_bundle+'_USER') in os.environ
           and ('BUNDLE_'+sftp_bundle+'_PASSWORD') in os.environ
           and ('BUNDLE_'+sftp_bundle+'_HOST') in os.environ):
            sftp_info['USER'] = os.environ['BUNDLE_'+sftp_bundle+'_USER']
            sftp_info['PASSWORD'] = os.environ['BUNDLE_'+sftp_bundle+'_PASSWORD']
            sftp_info['HOST'] = os.environ['BUNDLE_'+sftp_bundle+'_HOST']
            if 'BUNDLE_'+sftp_bundle+'_HOST_KEY' in os.environ:
                sftp_info['HOST-KEY'] = os.environ['BUNDLE_'+sftp_bundle+'_HOST_KEY']

        else:
            validate_required_fields(req, None, None, None,
                                     {'headers':['X-SFTP-HOST', 'X-SFTP-USER', 'X-SFTP-PASSWORD']})
            sftp_info['USER'] = req.get_header('X-SFTP-USER')
            sftp_info['PASSWORD'] = req.get_header('X-SFTP-PASSWORD')
            sftp_info['HOST'] = req.get_header('X-SFTP-HOST')
            if req.get_header('X-SFTP-HOST-KEY'):
                sftp_info['HOST-KEY'] = req.get_header('X-SFTP-HOST-KEY')

        return sftp_info
