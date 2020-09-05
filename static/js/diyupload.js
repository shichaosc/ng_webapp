(function ($) {
        $.fn.extend({
            diyUpload: function (opt, serverCallBack) {
                if (typeof opt != "object") {
                    alert('参数错误!');
                    return;
                }
                var $fileInput = $(this);
                var $fileInputId = $fileInput.attr('id');
                if (opt.url) {
                    opt.server = opt.url;
                    delete opt.url;
                }
                if (opt.success) {
                    var successCallBack = opt.success;
                    delete opt.success;
                }

                if (opt.error) {
                    var errorCallBack = opt.error;
                    delete opt.error;
                }
                $.each(getOption('#' + $fileInputId), function (key, value) {
                    opt[key] = opt[key] || value;
                });
                if (opt.buttonText) {
                    opt['pick']['label'] = opt.buttonText;
                    delete opt.buttonText;
                }
                var webUploader = getUploader(opt);
                if (!WebUploader.Uploader.support()) {
                    alert(' The upload component does not support your browser！');
                    return false;
                }
                webUploader.on('fileQueued', function (file) {
                    createBox($fileInput, file, webUploader);
                });
                webUploader.on('uploadProgress', function (file, percentage) {
                    var $fileBox = $('#fileBox_' + file.id);
                    var $diyBar = $fileBox.find('.diyBar');
                    $diyBar.show();
                    percentage = percentage * 100;
                    showDiyProgress(percentage.toFixed(2), $diyBar);
                });
                // 全部上传结束后触发;
                webUploader.on('uploadFinished', function () {

                    var session_data = $("#session_data").val();
                    $fileInput.next('.parentFileBox').children('.diyButton').remove();
                    alert("Uploaded successfully");
                    location.href = '/course/submithomework/?session_id=' + session_data;

                });
                webUploader.on('uploadAccept', function (object, data) {
                    if (serverCallBack)
                        serverCallBack(data);
                });
                webUploader.on('uploadSuccess', function (file, response) {
                    var $fileBox = $('#fileBox_' + file.id);
                    var $diyBar = $fileBox.find('.diyBar');
                    $fileBox.removeClass('diyUploadHover');
                    $diyBar.fadeOut(1000, function () {
                        $fileBox.children('.diySuccess').show();
                    });
                    if (successCallBack) {
                        successCallBack(response);
                    }
                });
                webUploader.on('uploadError', function (file, reason) {
                    var $fileBox = $('#fileBox_' + file.id);
                    var $diyBar = $fileBox.find('.diyBar');
                    showDiyProgress(0, $diyBar, 'Upload failed!');
                    var err = 'Upload failed! file:' + file.name + ' 错误码:' + reason;
                    if (errorCallBack) {
                        errorCallBack(err);
                    }
                });
                webUploader.on('error', function (code) {
                    var text = '';
                    switch (code) {
                        case 'F_DUPLICATE':
                            text = 'The file has been selected!';
                            break;
                        case 'Q_EXCEED_NUM_LIMIT':
                            text = 'The number of uploaded files exceeds the limit!';
                            break;
                        case 'F_EXCEED_SIZE':
                            text = 'File size over limit!';
                            break;
                        case 'Q_EXCEED_SIZE_LIMIT':
                            text = 'Total file size exceeded limit!';
                            break;
                        case 'Q_TYPE_DENIED':
                            text = 'File type is incorrect or empty!';
                            break;
                        default:
                            text = 'An unknown error!';
                            break;
                    }
                    alert(text);
                });
            }
        });




        function getUploader(opt) {
            return new WebUploader.Uploader(opt);
        }

        function showDiyProgress(progress, $diyBar, text) {
            if (progress >= 100) {
                progress = progress + '%';
                text = text || 'Upload to complete';
            } else {
                progress = progress + '%';
                text = text || progress;
            }
            var $diyProgress = $diyBar.find('.diyProgress');
            var $diyProgressText = $diyBar.find('.diyProgressText');
            $diyProgress.width(progress);
            $diyProgressText.text(text);
        }

    }
)(jQuery);
