const jqPromiseAjax = params => {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: params.url,
            type: params.type || 'get',
            dataType: 'json',
            headers: params.headers || {"content-type": "application/json"},
            data: params.data || {},
            success(res) {
                resolve(res)
            },
            error(err) {
                resolve('err')
            }
        })
    })
}

const upload = params => {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: params.url,
            type: "POST",
            processData: false,
            contentType: false,
            data: params.data,
            cache: false,
            success(res) {
                resolve(res)
            },
            error(err) {
                resolve('err')
            }
        })
    })
}
