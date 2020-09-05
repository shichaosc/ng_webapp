let defaultLessonSubjects = 8; // 默认有八道题
var hasReadQuestion = false;
var hasOtherQuestion = false;
var hasUploadSubject = false;
var isRequesting = false;
var outlineDataArr;
var knowledgeList;
let status = 'editing';
let typeToheaderlineAndDescription = {
    1:  {
            "headerline":"选择题",
            "description":"请选择正确的选项"
        },
    2:  {
            "headerline":"填空题",
            "description":"请在下划线处填上正确的答案"
        },
    3:  {
            "headerline":"连线题",
            "description":"点击汉字，选择它的拼音"
        },
    4:  {
            "headerline":"排序题",
            "description":"按照顺序点击下列内容"
        },
    5:  {
            "headerline":"阅读题",
            "description":"阅读短文回答问题"
        },
    6:  {
            "headerline":"其他",
            "description":"请完成之后拍照上传"
        }
};
let abcdef = {
    0 : "A. ",
    1 : "B. ",
    2 : "C. ",
    3 : "D. ",
    4 : "E. ",
    5 : "F. "
}
let editorList = {};
let outlineSubjectDomStr = (i) => ` <div class="form${i}" style="display: flex; align-items: center; padding-left: 10px; margin-bottom: 10px;">
                                        <span style="margin-right: 20px;">${i+1}. 题目类型：</span>
                                        <select name="" id="subject-${i}" style="margin-right: 30px;">
                                            <option value="1">选择题</option>
                                            <option value="2">填空题</option>
                                            <option value="3">连线题</option>
                                            <option value="4">排序题</option>
                                            <option value="5">阅读题</option>
                                            <option value="6">其他</option>
                                        </select>
                                        <span style="margin-right: 20px;">题目数量：</span>
                                        <input type="text" placeholder="请输入数字" class="subject-amount">
                                    </div>`;
let makeSubjectsPageTopButtons = ``;
let sortTitleDomStr = (type, lessonNo, headerline, description) => ` <div class="choice-subject-title">
                                                                        <div class="title-left">
                                                                            <strong class="headerline" id="headerline">${headerline?headerline:typeToheaderlineAndDescription[type].headerline}</strong>
                                                                            <span class="description" id="description">${description?description:typeToheaderlineAndDescription[type].description}</span>
                                                                        </div>
                                                                        <div class="title-right">
                                                                            <button id="edit-title-${lessonNo}" type="button" class="mr10">编辑</button>
                                                                            <button class="hidden change-outline" data-toggle="modal" data-target="#exampleModal"></button>
                                                                            <button class="mr10" id="delete-sort-${lessonNo}">删除这道大题</button>
                                                                        </div>
                                                                    </div>`;
let sortTitleDomStrInReadQuestion = (type, lessonNo, index, id, headerline, description) =>    `<div class="choice-subject-title">
                                                                                                    <div class="title-left">
                                                                                                        <strong id="headerline-${lessonNo}-${type}" class="mr20">${headerline?headerline:typeToheaderlineAndDescription[type].headerline}</strong>
                                                                                                        <span id="description-${lessonNo}-${type}">${description?description:typeToheaderlineAndDescription[type].description}</span>
                                                                                                    </div>
                                                                                                    <div class="title-right">
                                                                                                        <button id="edit-title-${lessonNo}-${type}-${index}-${id}" type="button" class="mr10">编辑</button>
                                                                                                        <button class="hidden change-outline" data-toggle="modal" data-target="#exampleModal"></button>
                                                                                                        <button class="mr10" id="delete-sort-${lessonNo}-${type}-${index}-${id}">删除这道题</button>
                                                                                                    </div>
                                                                                                </div>`;
let choiceQuestionsDomStr = (id, type, question, questionImage, rightAnswer, rightAnswerImage, otherAnswer, otherAnswerImage, lessonNo, isShowDeleteBtn) => 
    `<div class="choice-subject-body choice-subject-body-${id}">
        <div class="option option-stem">
            <div class="option-left">
                <span>${id+1}. 题干&nbsp;&nbsp;&nbsp;</span><input id="stem-${id}-${lessonNo}" type="text"  placeholder="点击输入" value=${question?question:''}>
            </div>
            <div class="option-right">
                <input type="button" value="上传图片" class="mr10" onclick="javascript:$($(this).siblings('input')).click();">
                <input type="file" accept="image/*" id="upload-image" class="hidden">
                <button id="delete-small-subject-${id}" class="${isShowDeleteBtn?'':'hidden'}">删除这道小题</button>
                <button id="knowledge-${lessonNo}-${id}-${type}">知识点设置</button>
                <button class="hidden" data-toggle="modal" data-target="#knowledge"></button>
            </div>
        </div>
        <div class="${questionImage?'':'hidden'} display chioce-stem-image mb20">
            <div class="option-left"><img src="${questionImage}" alt="" class="w100"></div>
            <div class="option-right"><button id="delete-stem-image-${lessonNo}-${id}">删除图片</button></div>
        </div>
        <div class="option right-option">
            <div class="option-left">
                <span>正确答案</span><input id="right-option-stem-${id}-${lessonNo}" type="text" placeholder="点击输入" value=${rightAnswer?rightAnswer:''}>
            </div>
            <div class="option-right">
                <input type="button" value="上传图片" onclick="javascript:$($(this).siblings('input')).click();">
                <input type="file" accept="image/*" id="upload-image" class="hidden">
            </div>
        </div>
        <div class="${rightAnswerImage?'':'hidden'} display chioce-stem-image mb20">
            <div class="option-left"><img src="${rightAnswerImage}" alt="" class="w100"></div>
            <div class="option-right"><button id="delete-right-answer-image-${lessonNo}-${id}">删除图片</button></div>
        </div>
        <div class="option first-other-option">
            <div class="option-left">
                <span>其他答案</span><input id="other-option-stem-${id}-${lessonNo}" type="text" placeholder="点击输入" value=${otherAnswer?otherAnswer:''}>
            </div>
            <div class="option-right">
                <input type="button" value="上传图片" onclick="javascript:$($(this).siblings('input')).click();">
                <input type="file" accept="image/*" id="upload-image" class="hidden">
            </div>
        </div>
        <div class="${otherAnswerImage?'':'hidden'} display chioce-stem-image mb20">
            <div class="option-left"><img src="${otherAnswerImage}" alt="" class="w100"></div>
            <div class="option-right"><button id="delete-other-answer-image-${lessonNo}-${id}">删除图片</button></div>
        </div>
        <div class="other-option-bag"></div>
        <div class="option add-other-option">
            <div class="option-left">
                <span class="opacity0">添加选项</span><input type="button" id="add-other-option-${id}" value="添加其他选项">
            </div>
            <div class="option-right">
            </div>
        </div>
    </div>`;
// 选择题其他选项
let otherOption = (lessonNo, index, id, value, image) =>  
    `<div class="option other-option-${id}">
        <div class="option-left">
            <span class="opacity0">其他答案</span><input id="other-option-text-${id}-${lessonNo}-${index}" type="text" placeholder="点击输入" value=${value?value:''}>
        </div>
        <div class="option-right">
            <input type="button" value="上传图片" class="mr10" onclick="javascript:$($(this).siblings('input')).click();"/>
            <input type="file" accept="image/*" id="other-option-image-${id}" class="hidden">
            <button id="delete-option-${id}">删除选项</button>
        </div>
    </div>
    <div class="${image?'':'hidden'} display chioce-stem-image mb20">
        <div class="option-left"><img src="${image}" alt="" class="w100"></div>
        <div class="option-right"><button id="delete-other-answer-image-${lessonNo}-${index}-${id}">删除图片</button></div>
    </div>`;
// 选择题其他选项
let otherOptionInReadQuestion = (lessonNo, index, id, i, ii, value, image) =>  `<div class="option other-option-${id}-${i}-${ii}">
                                                                                    <div class="option-left">
                                                                                        <span class="opacity0">其他答案</span><input id="other-option-text-${lessonNo}-${index}-${id}-${i}-${ii}" type="text" placeholder="点击输入" value=${value?value:''}>
                                                                                    </div>
                                                                                    <div class="option-right">
                                                                                        <input type="button" value="上传图片" class="mr10" onclick="javascript:$($(this).siblings('input[type=file]')).click();">
                                                                                        <input type="file" accept="image/*" id="upload-image" class="hidden">
                                                                                        <button id="delete-option-${lessonNo}-${index}-${id}-${i}-${ii}">删除选项</button>
                                                                                    </div>
                                                                                </div>
                                                                                <div class="${image?'':'hidden'} display chioce-stem-image mb20">
                                                                                    <div class="option-left"><img src="${image}" alt="" class="w100"></div>
                                                                                    <div class="option-right"><button id="delete-other-image-${lessonNo}-${index}-${id}-${i}-${ii}">删除图片</button></div>
                                                                                </div>`;
// 填空题每个小题div
let completionSubjectBodyDiv = (index) =>   `<div class="choice-subject-body completion-sunject-body-${index}"></div>`
// 填空题每个小题div
let completionSubjectBodyDivInReadQuestion = (lessonNo, id, i) =>   `<div class="choice-subject-body completion-sunject-body-${lessonNo}-${id}-${i}"></div>`
// 一组前句答案后句
let oneGroupBaseCompletion = (lessonNo, index, id, type, frontSentence, answer, endSentence) =>  
    `<div class="option">
        <div class="option-left">
            <span>${index+1}. 前句&nbsp;&nbsp;&nbsp;</span><input id="font-${lessonNo}-${index}-${id*3}" type="text" placeholder="点击输入" value=${frontSentence?frontSentence:""}>
        </div>
        <div class="option-right">
            <button id="delete-small-subject-${index}">删除这道小题</button>
            <button id="knowledge-${lessonNo}-${index}-${type}">知识点设置</button>
            <button class="hidden" data-toggle="modal" data-target="#knowledge"></button>
        </div>
    </div>
    <div class="option">
        <div class="option-left">
            <span>正确答案</span><input id="right-answer-${lessonNo}-${index}-${id*3+1}" type="text" placeholder="点击输入" value=${answer?answer:""}>
        </div>
        <div class="option-right">
        </div>
    </div>
    <div class="option first-other-option">
        <div class="option-left">
            <span>后句&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><input id="end-${lessonNo}-${index}-${id*3+2}" type="text" placeholder="点击输入" value=${endSentence?endSentence:""}>
        </div>
        <div class="option-right">
        </div>
    </div>`;
// 一组前句答案后句
let oneGroupBaseCompletionInReadQuestion = (lessonNo, index, id, i, ii, type, frontSentence, answer, endSentence) =>  `<div class="option">
                                                                                                <div class="option-left">
                                                                                                    <span>${i+1}. 前句&nbsp;&nbsp;&nbsp;</span><input id="font-${lessonNo}-${index}-${id*3}-${i}-${ii}" type="text" placeholder="点击输入" value=${frontSentence?frontSentence:""}>
                                                                                                </div>
                                                                                                <div class="option-right">
                                                                                                </div>
                                                                                            </div>
                                                                                            <div class="option">
                                                                                                <div class="option-left">
                                                                                                    <span>正确答案</span><input id="right-answer-${lessonNo}-${index}-${id*3+1}-${i}-${ii}" type="text" placeholder="点击输入" value=${answer?answer:""}>
                                                                                                </div>
                                                                                                <div class="option-right">
                                                                                                </div>
                                                                                            </div>
                                                                                            <div class="option first-other-option">
                                                                                                <div class="option-left">
                                                                                                    <span>后句&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><input id="end-${lessonNo}-${index}-${id*3+2}-${i}-${ii}" type="text" placeholder="点击输入" value=${endSentence?endSentence:""}>
                                                                                                </div>
                                                                                                <div class="option-right">
                                                                                                </div>
                                                                                            </div>`;
let oneGroupCompletion = (lessonNo, index, id, frontSentence, answer, endSentence) =>  `<div class="option">
                                                                                            <div class="option-left">
                                                                                                <span> 前句&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><input id="font-${lessonNo}-${index}-${id*3}" type="text" placeholder="点击输入" value=${frontSentence?frontSentence:""}>
                                                                                            </div>
                                                                                            <div class="option-right">
                                                                                            </div>
                                                                                        </div>
                                                                                        <div class="option">
                                                                                            <div class="option-left">
                                                                                                <span>正确答案</span><input id="right-answer-${lessonNo}-${index}-${id*3+1}" type="text" placeholder="点击输入" value=${answer?answer:""}>
                                                                                            </div>
                                                                                            <div class="option-right">
                                                                                            </div>
                                                                                        </div>
                                                                                        <div class="option first-other-option">
                                                                                            <div class="option-left">
                                                                                                <span>后句&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><input id="end-${lessonNo}-${index}-${id*3+2}" type="text" placeholder="点击输入" value=${endSentence?endSentence:""}>
                                                                                            </div>
                                                                                            <div class="option-right">
                                                                                            </div>
                                                                                        </div>`;
let oneGroupCompletionInReadQuestion = (lessonNo, index, id, i, ii, frontSentence, answer, endSentence) =>  `<div class="option">
                                                                                                            <div class="option-left">
                                                                                                                <span> 前句&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><input id="font-${lessonNo}-${index}-${id*3}-${i}-${ii}" type="text" placeholder="点击输入" value=${frontSentence?frontSentence:""}>
                                                                                                            </div>
                                                                                                            <div class="option-right">
                                                                                                            </div>
                                                                                                        </div>
                                                                                                        <div class="option">
                                                                                                            <div class="option-left">
                                                                                                                <span>正确答案</span><input id="right-answer-${lessonNo}-${index}-${id*3+1}-${i}-${ii}" type="text" placeholder="点击输入" value=${answer?answer:""}>
                                                                                                            </div>
                                                                                                            <div class="option-right">
                                                                                                            </div>
                                                                                                        </div>
                                                                                                        <div class="option first-other-option">
                                                                                                            <div class="option-left">
                                                                                                                <span>后句&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><input id="end-${lessonNo}-${index}-${id*3+2}-${i}-${ii}" type="text" placeholder="点击输入" value=${endSentence?endSentence:""}>
                                                                                                            </div>
                                                                                                            <div class="option-right">
                                                                                                            </div>
                                                                                                        </div>`;
// 填空题添加其他选项
let completeAddOtherOptionBtn = (lessonNo, index) =>   `<div class="option add-other-option">
                                                            <div class="option-left">
                                                                <span class="opacity0">添加&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><input type="button" id="add-complete-${lessonNo}-${index}" value="添加其他选项">
                                                            </div>
                                                            <div class="option-right">
                                                            </div>
                                                        </div>`;
// 填空题添加其他选项
let completeAddOtherOptionBtnInReadQuestion = (lessonNo, index, id, i, type) => `<div class="option add-other-option">
                                                                                    <div class="option-left">
                                                                                        <span class="opacity0">添加&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><input type="button" id="add-complete-${lessonNo}-${index}-${id}-${i}-${type}" value="添加其他选项">
                                                                                    </div>
                                                                                    <div class="option-right">
                                                                                    </div>
                                                                                </div>`;
// 连线题第一组
let connectionBaseGroup = (lessonNo, index, type, question, questionImage, answer, answerImage, isShowAddBtn) =>    `<div class="choice-subject-body connection-subject-body-${index} mt50">
                                                                                                                        <div class="option option-${lessonNo}-${index}-0">
                                                                                                                            <div class="option-left flex">
                                                                                                                                <div class="flex1 flex">
                                                                                                                                    <span>${index+1}.&nbsp;&nbsp;&nbsp;</span>
                                                                                                                                    <input id="stem-${lessonNo}-${index}-0" type="text" placeholder="点击输入" class="flex1" value=${question?question:''}>
                                                                                                                                    <div class="connection-add-image">
                                                                                                                                        <button class="head-add-image" onclick="javascript:$($(this).siblings('input[type=file]')).click();">添加图片</button>
                                                                                                                                        <input type="file" accept="image/*" id="upload-image" class="hidden">
                                                                                                                                    </div>
                                                                                                                                </div>
                                                                                                                                <div class="flex1 flex">
                                                                                                                                    <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;正确答案&nbsp;&nbsp;&nbsp;</span>
                                                                                                                                    <input id="answer-${lessonNo}-${index}-0" type="text" placeholder="点击输入" class="flex1" value=${answer?answer:''}>
                                                                                                                                    <div class="connection-add-image">
                                                                                                                                        <button class="end-add-image" onclick="javascript:$($(this).siblings('input[type=file]')).click();">添加图片</button>
                                                                                                                                        <input type="file" accept="image/*" id="upload-image" class="hidden w100">
                                                                                                                                    </div>
                                                                                                                                </div>
                                                                                                                            </div>
                                                                                                                            <div class="option-right">
                                                                                                                                <button id="delete-small-subject-${index}">删除这道小题</button>
                                                                                                                                <button id="knowledge-${lessonNo}-${index}-${type}">知识点设置</button>
                                                                                                                                <button class="hidden" data-toggle="modal" data-target="#knowledge"></button>
                                                                                                                                <button id="add-group-${lessonNo}-${index}" class=${isShowAddBtn?'':'hidden'}>增加一组连线</button>
                                                                                                                            </div>
                                                                                                                        </div>
                                                                                                                        <div class="flex mb20 ${questionImage || answerImage?'':'hidden'}">
                                                                                                                            <div class="option-left pl20 display">
                                                                                                                                <div class="flex1">
                                                                                                                                    <img src="${questionImage}" class="${questionImage?'':'hidden'} flex1 w100">
                                                                                                                                    <button id="delete-image-${lessonNo}-${index}-0-0" class="${questionImage?'':'hidden'}">删除图片</button>
                                                                                                                                </div>
                                                                                                                                <div class="flex1 pl150 ${answerImage?'':'hidden'}">
                                                                                                                                    <img src="${answerImage}" class="${answerImage?'':'hidden'} flex1 w100">
                                                                                                                                    <button id="delete-image-${lessonNo}-${index}-0-1" class="${answerImage?'':'hidden'}">删除图片</button>
                                                                                                                                </div>
                                                                                                                                
                                                                                                                            </div>
                                                                                                                            <div class="option-right">
                                                                                                                            </div>
                                                                                                                        </div>
                                                                                                                    </div>`;
// 连线题其他组
let connectionOtherGroup = (lessonNo, index, id, question, questionImage, answer, answerImage, isShowAddBtn) =>  `<div class="option option-${lessonNo}-${index}-${id}">
                                                                                                                    <div class="option-left flex">
                                                                                                                        <div class="flex1 flex">
                                                                                                                            <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                                                                                                                            <input id="stem-${lessonNo}-${index}-${id}" type="text" placeholder="点击输入" class="flex1" value=${question?question:''}>
                                                                                                                            <div class="connection-add-image">
                                                                                                                                <button class="head-add-image" onclick="javascript:$($(this).siblings('input[type=file]')).click();">添加图片</button>
                                                                                                                                <input type="file" accept="image/*" id="upload-image" class="hidden">
                                                                                                                            </div>
                                                                                                                        </div>
                                                                                                                        <div class="flex1 flex">
                                                                                                                            <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;正确答案&nbsp;&nbsp;&nbsp;</span>
                                                                                                                            <input id="answer-${lessonNo}-${index}-${id}" type="text" placeholder="点击输入" class="flex1" value=${answer?answer:''}>
                                                                                                                            <div class="connection-add-image">
                                                                                                                                <button class="end-add-image" onclick="javascript:$($(this).siblings('input[type=file]')).click();">添加图片</button>
                                                                                                                                <input type="file" accept="image/*" id="upload-image" class="hidden">
                                                                                                                            </div>
                                                                                                                        </div>
                                                                                                                    </div>
                                                                                                                    <div class="option-right">
                                                                                                                        <button id="delete-group-${lessonNo}-${index}-${id}" class=${id == 1?'hidden':''}>删除这组连线</button>
                                                                                                                        <button id="add-group-${lessonNo}-${index}" class=${isShowAddBtn?'':'hidden'}>增加一组连线</button>
                                                                                                                    </div>
                                                                                                                </div>
                                                                                                                <div class="flex mb20 ${questionImage || answerImage?'':'hidden'}">
                                                                                                                    <div class="option-left pl20 display">
                                                                                                                        <div class="flex1">
                                                                                                                            <img src="${questionImage}" class="${questionImage?'':'hidden'} flex1 w100">
                                                                                                                            <button id="delete-image-${lessonNo}-${index}-${id}-0" class="${questionImage?'':'hidden'}">删除图片</button>
                                                                                                                        </div>
                                                                                                                        <div class="flex1 pl150">
                                                                                                                            <img src="${answerImage}" class="${answerImage?'':'hidden'} flex1 w100">
                                                                                                                            <button id="delete-image-${lessonNo}-${index}-${id}-1" class="${answerImage?'':'hidden'}>删除图片</button>
                                                                                                                        </div>
                                                                                                                        
                                                                                                                    </div>
                                                                                                                    <div class="option-right">
                                                                                                                    </div>
                                                                                                                </div>`
// 改变大题名称描述
let changeTitleInfo = (type, headerline, description, amount, readOnly) =>  ` <div class="change-headerline mb20 h40 lh40 flex">
                                                                        <span>类型名称：</span><input type="text" class="flex1 change-headerline-input" placeholder="点击输入" value=${headerline?headerline:typeToheaderlineAndDescription[type].headerline}>
                                                                    </div>
                                                                    <div class="change-description h40 lh40 flex mb40">
                                                                        <span>类型描述：</span><input type="text" class="flex1 change-description-input" placeholder="点击输入" value=${description?description:typeToheaderlineAndDescription[type].description}>
                                                                    </div>
                                                                    <div class="h40 lh40 flex">
                                                                        <span>题目数量：</span><input type="number" class="change-quanlity-input" placeholder="点击输入" value=${amount} ${readOnly?readonly='readonly':''}>
                                                                    </div>`;
let sortBaseSubject = (lessonNo, index, type, preSentence, endSentence) =>  `<div class="choice-subject-body sort-subject-body-${index} mt50">
                                                                        <div class="option">
                                                                            <div class="option-left">
                                                                                <span>${index+1}. 前句</span><input id="pre-sentence-${lessonNo}-${index}" type="text"  placeholder="点击输入" value=${preSentence?preSentence:''}>
                                                                            </div>
                                                                            <div class="option-right">
                                                                                <button id="delete-small-subject-${index}">删除这道小题</button>
                                                                                <button id="knowledge-${lessonNo}-${index}-${type}">知识点设置</button>
                                                                                <button class="hidden" data-toggle="modal" data-target="#knowledge"></button>
                                                                            </div>
                                                                        </div>
                                                                        <div class="option right-option">
                                                                            <div class="option-left">
                                                                                <span>&nbsp;&nbsp;&nbsp;&nbsp;后句</span><input id="post-sentence-stem-${lessonNo}-${index}" type="text" placeholder="点击输入" value=${endSentence?endSentence:''}>
                                                                            </div>
                                                                            <div class="option-right">
                                                                            </div>
                                                                        </div>
                                                                    </div>`;
let sortOtherItem = (lessonNo, index, id, sortNo, sortContent, isShowDeleteBtn, isShowAddBtn) => `<div class="option">
                                                    <div class="option-left">
                                                        <span>排序${sortNo}</span><input id="other-sort-stem-${lessonNo}-${index}-${id}" type="text" placeholder="点击输入" value=${sortContent?sortContent:''}>
                                                    </div>
                                                    <div class="option-right">
                                                        <button id="delete-sentence-${lessonNo}-${index}-${id}" class=${isShowDeleteBtn?'':'hidden'}>删除这条语句</button>
                                                        <button id="add-sentence-${lessonNo}-${index}" class=${isShowAddBtn?'':'hidden'}>增加一条语句</button>
                                                    </div>
                                                </div>`;
let richTextBaseItem = (lessonNo, index, type) => `<div class="choice-subject-body richtext-${lessonNo}-${index}">
                                                <div class="flex">
                                                    <div class="option-left">
                                                        <span>${index+1}. 短文</span>
                                                    </div>
                                                    <div class="option-right">
                                                        <button id="delete-small-subject-${index}">删除这道小题</button>
                                                        <button id="knowledge-${lessonNo}-${index}-${type}">知识点设置</button>
                                                        <button class="hidden" data-toggle="modal" data-target="#knowledge"></button>
                                                    </div>
                                                </div>
                                                <div class="article"></div>
                                             </div>`;
// i: 第几道选择题
let choiceQuestionsInReadQuestionDomStr = (lessonNo, index, i, type, question, questionImage, rightAnswer, rightAnswerImage, otherAnswer, otherAnswerImage) => 
                                                    `<div class="choice-subject-body choice-subject-body-${lessonNo}-${type}-${i}">
                                                        <div class="option option-stem-${i}">
                                                            <div class="option-left">
                                                                <span>${i+1}. 题干&nbsp;&nbsp;&nbsp;</span><input id="stem-${lessonNo}-${index}-${type}-${i}" type="text"  placeholder="点击输入" value=${question?question:''}>
                                                            </div>
                                                            <div class="option-right">
                                                                <input type="button" value="上传图片" class="mr10" onclick="javascript:$($(this).siblings('input[type=file]')).click();">
                                                                <input type="file" accept="image/*" id="upload-image" class="hidden">
                                                            </div>
                                                        </div>
                                                        <div class="${questionImage?'':'hidden'} display chioce-stem-image mb20">
                                                            <div class="option-left"><img src="${questionImage}" alt="" class="w100"></div>
                                                            <div class="option-right"><button id="delete-stem-image-${lessonNo}-${index}-${i}">删除图片</button></div>
                                                        </div>
                                                        <div class="option right-option">
                                                            <div class="option-left">
                                                                <span>正确答案</span><input id="right-option-stem-${lessonNo}-${index}-${type}-${i}" type="text" placeholder="点击输入" value=${rightAnswer?rightAnswer:''}>
                                                            </div>
                                                            <div class="option-right">
                                                                <input type="button" value="上传图片" onclick="javascript:$($(this).siblings('input[type=file]')).click();">
                                                                <input type="file" accept="image/*" id="upload-image" class="hidden">
                                                            </div>
                                                        </div>
                                                        <div class="${rightAnswerImage?'':'hidden'} display chioce-stem-image mb20">
                                                            <div class="option-left"><img src="${rightAnswerImage}" alt="" class="w100"></div>
                                                            <div class="option-right"><button id="delete-right-image-${lessonNo}-${index}--${i}">删除图片</button></div>
                                                        </div>
                                                        <div class="option first-other-option-${i}">
                                                            <div class="option-left">
                                                                <span>其他答案</span><input id="other-option-stem-${lessonNo}-${index}-${type}-${i}" type="text" placeholder="点击输入" value=${otherAnswer?otherAnswer:''}>
                                                            </div>
                                                            <div class="option-right">
                                                                <input type="button" value="上传图片" onclick="javascript:$($(this).siblings('input[type=file]')).click();">
                                                                <input type="file" accept="image/*" id="upload-image" class="hidden">
                                                            </div>
                                                        </div>
                                                        <div class="${otherAnswerImage?'':'hidden'} display chioce-stem-image mb20">
                                                            <div class="option-left"><img src="${otherAnswerImage}" alt="" class="w100"></div>
                                                            <div class="option-right"><button id="delete-other-image-${lessonNo}-${index}-${type}-${i}">删除图片</button></div>
                                                        </div>
                                                        <div class="other-option-bag"></div>
                                                        <div class="option add-other-option">
                                                            <div class="option-left">
                                                                <span class="opacity0">添加选项</span><input type="button" id="add-other-option-${lessonNo}-${index}-${type}-${i}" value="添加其他选项">
                                                            </div>
                                                            <div class="option-right">
                                                            </div>
                                                        </div>
                                                    </div>`;
let knowledgeDomStr = (type) => `<div class="mb20"><span>题目类型：${typeToheaderlineAndDescription[type].headerline}</span></div>
                                <div class="content">
                                    <span>考查内容：</span>
                                </div>`;
let addAdjustSubjectItem = (lessonNo, type) =>  `<div class="subject-info-left pl20 flex">
                                                    <select name="" id="" class="mr20 select-${lessonNo}">
                                                        <option value="1" ${type==1?'selected':''}>选择题</option>
                                                        <option value="2" ${type==2?'selected':''}>填空题</option>
                                                        <option value="3" ${type==3?'selected':''}>连线题</option>
                                                        <option value="4" ${type==4?'selected':''}>排序题</option>
                                                        <option value="5" ${type==5?'selected':''}>阅读题</option>
                                                        <option value="6" ${type==6?'selected':''}>其他</option>
                                                    </select>
                                                    <input type="text" style="width:40px;" class="input-${lessonNo}">
                                                </div>`;
let adjustSubjectItem = (type, number) =>  `<div class="subject-info-left pl20">
                                                <span class="mr20">${typeToheaderlineAndDescription[type].headerline}</span>
                                                <span>${number}道</span>
                                            </div>`;
let adjustmentBtns = (lessonNo) => `<div class="subject-info-right pr20">
                                        <button class="mr20 up-btn-${lessonNo}">上移</button>
                                        <button class="mr20 down-btn-${lessonNo}">下移</button>
                                        <button class="mr20 add-btn-${lessonNo}">插入一道大题</button>
                                        <button class="mr20 delete-btn-${lessonNo}">删除这道大题</button>
                                    </div>`;
let adjustmentDomStr = (id) => `<div class="subject-info-brief flex mb20 adjustment-${id}"></div>`
let examination = () => {
    let str = "<select name='' id='' class='mr20'>";
    knowledgeList.forEach((item, index) => {
        str += `<option value=${item.id}>${item.label}</option>`
    })
    str += "</select><span>备注：</span><input type='text'>";
    return str;
}
let section = (lessonNo) => `<section class="choice-subject-${lessonNo}"></section>`;
let subjestsIdAndDonStr = {
    1: choiceQuestionsDomStr,
    2: oneGroupBaseCompletion,
    3: oneGroupBaseCompletion,
    4: oneGroupBaseCompletion,
    5: oneGroupBaseCompletion
}
let typeToData = {
    1:  {
            "question": "", 
            "questionImage": "", 
            "options": 
                [{
                    "answer": "", 
                    "answerImage": ""
                }, 
                {
                    "answer": "", 
                    "answerImage": ""
                },
                {
                    "answer": "", 
                    "answerImage": ""
                },
                {
                    "answer": "", 
                    "answerImage": ""
                }]
        },
    2:  {
            "options": 
                [{
                    "sentence": "",
                    "rightFlag": 0
                },
                {
                    "sentence": "", 
                    "rightFlag": 1
                },
                {
                    "sentence": "", 
                    "rightFlag": 0
                }]
        },
    3:  {
            "options": 
                [{
                    "head": "", 
                    "headImage": "", 
                    "tail": "", 
                    "tailImage": ""
                },
                {
                    "head": "", 
                    "headImage": "", 
                    "tail": "", 
                    "tailImage": ""
                },
                {
                    "head": "", 
                    "headImage": "", 
                    "tail": "", 
                    "tailImage": ""
                },
                {
                    "head": "", 
                    "headImage": "", 
                    "tail": "", 
                    "tailImage": ""
                }
                ]
        },
    4:  {
            "pre": "", 
            "post": "", 
            "options": 
                [{
                    "word": ""
                }, 
                {
                    "word": ""
                }, 
                {
                    "word": ""
                }, 
                {
                    "word": ""
                }]
        },
    5:  {
            "htmlArticle": ""
        },
    6:  {
            "fileUrl": "", 
            "fileType": ""
        }
};
let queryObj = {
    'lessonId': null,
    'type': null
};
var sortObj = {
    0: "①",
    1: "②",
    2: "③",
    3: "④",
    4: "⑤"
};

// 上传图片
async function uploadImage(file) {
    let imageData = new FormData();
    imageData.append('image_file', file);
    startLoading();
    let imageUrl = await upload({
        url: `/homework/question/upload_question_img/`,
        data: imageData
    })
    endLoading();

    if (imageUrl != 'err') {
        return imageUrl.data;
    } else {
        alert('上传失败')
    }
    
}

// 上传老版本作业
async function uploadFile(data) {
    startLoading();
    let imageUrl = await upload({
        url: `/man/course/homeworkupload/`,
        data: data
    })
    endLoading();
       
    if (imageUrl != 'err') {
        return true;
    } else {
        alert('上传失败')
    }
}

// 修改大题名称描述
async function changeTitle(id, name, remark) {
    let result = await jqPromiseAjax({
        url: `/homework/outline_group/${id}/`,
        type: 'PUT',
        data: JSON.stringify({
            'name': name,
            'remark': remark
        })
    })
    return result;
}

// 删除大纲
async function deleteOutline(id) {
    let result = await jqPromiseAjax({
        url: `/homework/outline_group/${id}/`,
        type: 'DELETE',
    })
    isRequesting = false;
    return result;
}

// 删除小题
async function deleteSmallSubject(id) {
    let result = await jqPromiseAjax({
        url: `/homework/question/${id}/`,
        type: 'DELETE',
    })
    return result;
}

// 获取本节课大纲
async function getOutline(lessonId, renderType) {
    let submitResult = await jqPromiseAjax({
        url: `/homework/outline_group/?lesson_id=${lessonId}&ordering=sort_no`,
    })
    if (submitResult != 'err') {
        if (submitResult.length > 0) {
            outlineDataArr = submitResult;
            console.log(JSON.stringify(outlineDataArr))
            if (renderType == 0) {
                renderMakeSubjects();
            } else {
                renderPreviewModal();
            }
            return true;
        } else {
            alert("这节课没有创建家庭作业")
        }
    } else {
        alert("获取题目失败")
    }
}

// 调整大纲
async function adjustOutline(data) {
    let adjustResult = await jqPromiseAjax({
        url: `/homework/outline_group/update_outlines/`,
        type: 'POST',
        data: JSON.stringify(data)
    })
    return adjustResult;
}

// 设置知识点
async function setKnowledgePoint(data) {
    let pointResult = await jqPromiseAjax({
        url: `/homework/outline/edit_outline/`,
        type: 'POST',
        data: JSON.stringify(data)
    })

    if (pointResult.code != 0) {
        alert("设置失败")
    } else {
        return true;
    }
}

// 发布作业
async function publishHomework(id) {
    let publishResult = await jqPromiseAjax({
        url: '/homework/outline/publish/',
        type: 'POST',
        data: JSON.stringify({lesson_id: id})
    })

    if (publishResult != 'err' && publishResult.code != 0) {
        alert('发布成功')
    } else {
        alert('发布成功')
    }
}

// 判断这节课有没有题
async function hasSubject(lesson_id) {
    let result = await jqPromiseAjax({
        url: `/homework/outline/exists/?lesson_id=${lesson_id}`,
    })

    if (result.data.exist == 1) {
        return true;
    } else {
        return false;
    }
}

// 初始渲染8道大纲题数
function renderSubjects() {
    let subjectDom = '';
    for(let i = 0; i < 8; i++) {
        subjectDom += outlineSubjectDomStr(i)
    }
    $(".outline-content").append($(subjectDom));
}

// 绑定事件清除
function removeEventListener() {

        $("#save-knowledge").unbind();
}

// 上传图片并更改数据
async function uploadImageAndUpdateData(file) {
    if (file.size > 204800) {
        $(this).val("")
        alert("图片必须小于200kb")
    } else {
        let result = await uploadImage(file);
        return result;
    }

}

// 制作题目页面事件绑定
function bindingMakeSubjectsEvent() {
    for (let lessonNo in outlineDataArr) {
        // 修改大题题目
        $(`.choice-subject-${outlineDataArr[lessonNo].id} #edit-title-${lessonNo}`).click(function () {
            // 显示弹框
            $("#exampleModal .modal-body").append(changeTitleInfo(outlineDataArr[lessonNo].type, outlineDataArr[lessonNo].name, outlineDataArr[lessonNo].remark, outlineDataArr[lessonNo].homework_question.length, outlineDataArr[lessonNo].type==5||outlineDataArr[lessonNo].type==6?true:false))
            $(this).siblings(`button.change-outline`).trigger("click");
            // 保存修改的大纲
            $(".sava-change").click(async function() {
                let subjectNumber = Number($(".change-quanlity-input").val()),
                    name = $(".change-headerline-input").val(),
                    remark = $(".change-description-input").val();

                // 改变大纲题目quality 
                if (subjectNumber <= 0) {
                    let result = await deleteOutline(outlineDataArr[lessonNo].id);
                    if (result == 'err') {
                        alert('操作失败');
                        return;
                    }
                    outlineDataArr.splice(lessonNo, 1);
                    readAllValue();
                } else {
                    // 减少这道大题的小题数量
                    let subjectLength = outlineDataArr[lessonNo].homework_question.length;
                    if ( subjectLength > subjectNumber) {
                        for (let i = subjectLength-1; i > subjectNumber-1; i--) {
                            let lastSubject = outlineDataArr[lessonNo].homework_question[i];
                            if (lastSubject.id) {
                                let result = await deleteSmallSubject(lastSubject.id);
                                if (result == 'err') {
                                    alert('操作失败');
                                    return;
                                }
                            }
                            outlineDataArr[lessonNo].homework_question.pop()
                        }
                        outlineDataArr[lessonNo].quality = Number($(".change-quanlity-input").val());
                        readAllValue();
                    } else {
                        readAllValue();
                        // 增加这道大题的小题数量
                        for (let i = outlineDataArr[lessonNo].homework_question.length; i < subjectNumber; i++) {
                            let obj = {};
                            obj['other_option_quality'] = 3;
                            obj['content'] = JSON.parse(JSON.stringify(typeToData[outlineDataArr[lessonNo].type]));
                            outlineDataArr[lessonNo].homework_question.push(obj);
                        }
                        outlineDataArr[lessonNo].quality = Number($(".change-quanlity-input").val());
                    }
                    // 改变大纲题目name remark      
                    if (outlineDataArr[lessonNo].name != name || outlineDataArr[lessonNo].remark != remark) {
                        let result = await changeTitle(outlineDataArr[lessonNo].id, name, remark);
                        if (result == 'err') {
                            alert('操作失败');
                            return;
                        }
                        outlineDataArr[lessonNo].name = name;
                        outlineDataArr[lessonNo].remark = remark;
                    }
                }
                
                
                $('#exampleModal').modal('hide');
                $("#exampleModal .modal-body").children().remove();
                removeEventListener();

                renderMakeSubjects();
            })

            $('#exampleModal').on('hidden.bs.modal', () => {
                $("#exampleModal .modal-body").children().remove();
                $(".sava-change").unbind();
            })
        })

        // 删除这道大题
        $(`.choice-subject-${outlineDataArr[lessonNo].id} #delete-sort-${lessonNo}`).click(async function() {
            let result = await deleteOutline(outlineDataArr[lessonNo].id);
            if (result == 'err') {
                alert('操作失败');
                return;
            }
            readAllValue();
            outlineDataArr.splice(lessonNo, 1);
            renderMakeSubjects();
        })

        // 删除这道小题
        for (let index in outlineDataArr[lessonNo].homework_question) {
            $(`.choice-subject-${outlineDataArr[lessonNo].id} #delete-small-subject-${index}`).click(async function() {
                if (outlineDataArr[lessonNo].homework_question.length == 1) {
                    $(`.choice-subject-${outlineDataArr[lessonNo].id} #delete-sort-${lessonNo}`).trigger("click");
                } else {
                    if (outlineDataArr[lessonNo].homework_question[index].id) {
                        let result = await deleteSmallSubject(outlineDataArr[lessonNo].homework_question[index].id);
                        if (result == 'err') {
                            alert('操作失败');
                            return;
                        }
                    }

                    readAllValue();
                    outlineDataArr[lessonNo].homework_question.splice(index, 1);
                    renderMakeSubjects();
                }
            })
        }

        // 选择题
        if (outlineDataArr[lessonNo].type == 1) {
            for (let i = 0; i < outlineDataArr[lessonNo].homework_question.length; i++) {
                // 选择题题干图片上传
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} .option-stem input[type=file]`).change(async function(e) {
                    let image = await uploadImageAndUpdateData(e.target.files[0]);
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[i].content.questionImage = image;
                    renderMakeSubjects();
                })

                // 选择题题干图片删除
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} #delete-stem-image-${lessonNo}-${i}`).click(async function(e) {
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[i].content.questionImage = '';
                    renderMakeSubjects();
                })

                // 选择题正确答案图片上传
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} .right-option input[type=file]`).change(async function(e) {
                    let image = await uploadImageAndUpdateData(e.target.files[0]);
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[i].content.options[0].answerImage = image;
                    renderMakeSubjects();
                })

                // 选择题题干图片删除
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} #delete-right-answer-image-${lessonNo}-${i}`).click(async function(e) {
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[i].content.options[0].answerImage = '';
                    renderMakeSubjects();
                })

                // 第一个其他选项图片上传
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} .first-other-option input[type=file]`).change(async function(e) {
                    let image = await uploadImageAndUpdateData(e.target.files[0]);
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[i].content.options[1].answerImage = image;
                    renderMakeSubjects();
                })
                // 第一个其他选项图片删除
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} #delete-other-answer-image-${lessonNo}-${i}`).click(async function(e) {
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[i].content.options[1].answerImage = '';
                    renderMakeSubjects();
                })
                
                // 知识点设置
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} #knowledge-${lessonNo}-${i}-1`).click(function() {
                    $(this).siblings("button.hidden").trigger("click");
                    $('#knowledge .modal-body').append(knowledgeDomStr(1));
                    $('#knowledge .modal-body .content').append(examination());

                    $("#save-knowledge").click(function() {
                        outlineDataArr[lessonNo].homework_question[i].content['knowledge_point_id'] = $('#knowledge option:selected').val();
                        outlineDataArr[lessonNo].homework_question[i].content['knowledge_point_remark'] = $('#knowledge input').val();
                        $('#knowledge').modal('hide');
                        $("#knowledge .modal-body").children().remove();
                    })

                    $('#knowledge').on('hidden.bs.modal', () => {
                        $("#knowledge .modal-body").children().remove();
                    })
                })
                for (let j = 2; j < outlineDataArr[lessonNo].homework_question[i].content.options.length+1; j++) {
                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} .other-option-bag #delete-option-${j}`).click(function() {
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[i].content.options.splice(j, 1);
                        // outlineDataArr[lessonNo].homework_question[i].other_option_quality--;
                        renderMakeSubjects();
                    })

                    // 其他选项图片上传
                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} .other-option-bag .other-option-${j} input[type=file]`).change(async function(e) {
                        let image = await uploadImageAndUpdateData(e.target.files[0]);
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[i].content.options[j].answerImage = image;
                        renderMakeSubjects();
                    })

                    // 其他选项图片上传
                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} .other-option-bag #delete-other-answer-image-${lessonNo}-${i}-${j}`).click(async function(e) {
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[i].content.options[j].answerImage = '';
                        renderMakeSubjects();
                    })
                
                }
            }
            // 添加其他选项
            for (let i = 0; i < outlineDataArr[lessonNo].quality; i++) {
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .choice-subject-body-${i} #add-other-option-${i}`).click(function() {
                    if (outlineDataArr[lessonNo].homework_question[i].content.options.length == 6) {
                        alert("选择题选项为2-6个")
                    } else {
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[i].content.options.push(JSON.parse((JSON.stringify(typeToData[1]))));
                        renderMakeSubjects();
                    }
                })
            }
        } else if (outlineDataArr[lessonNo].type == 2) { // 填空题
            for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {

                // 知识点设置
                $(`.choice-subject-${outlineDataArr[lessonNo].id} #knowledge-${lessonNo}-${index}-2`).click(function() {
                    $(this).siblings("button.hidden").trigger("click");
                    $('#knowledge .modal-body').append(knowledgeDomStr(2));
                    $('#knowledge .modal-body .content').append(examination());

                    $("#save-knowledge").click(function() {
                        outlineDataArr[lessonNo].homework_question[index].content['knowledge_point_id'] = $('#knowledge option:selected').val();
                        outlineDataArr[lessonNo].homework_question[index].content['knowledge_point_remark'] = $('#knowledge input').val();
                        $('#knowledge').modal('hide');
                        $("#knowledge .modal-body").children().remove();
                    })

                    $('#knowledge').on('hidden.bs.modal', () => {
                        $("#knowledge .modal-body").children().remove();
                    })
                })
                
                
                $(`.choice-subject-${outlineDataArr[lessonNo].id} .completion-sunject-body-${index} #add-complete-${lessonNo}-${index}`).click(function() {
                    if (outlineDataArr[lessonNo].homework_question[index].content.options.length == 15) {
                        alert("填空题最多只能有5个填空");
                        return;
                    }
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[index].content.options = outlineDataArr[lessonNo].homework_question[index].content.options.concat(JSON.parse((JSON.stringify(typeToData[2].options))));
                    // outlineDataArr[lessonNo].homework_question[index].group_number++;
                    renderMakeSubjects();
                })
            }
        } else if (outlineDataArr[lessonNo].type == 3) { // 连线题
            for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {

                // 知识点设置
                $(`.choice-subject-${outlineDataArr[lessonNo].id} #knowledge-${lessonNo}-${index}-3`).click(function() {
                    $(this).siblings("button.hidden").trigger("click");
                    $('#knowledge .modal-body').append(knowledgeDomStr(3));
                    $('#knowledge .modal-body .content').append(examination());

                    $("#save-knowledge").click(function() {
                        outlineDataArr[lessonNo].homework_question[index].content['knowledge_point_id'] = $('#knowledge option:selected').val();
                        outlineDataArr[lessonNo].homework_question[index].content['knowledge_point_remark'] = $('#knowledge input').val();
                        $('#knowledge').modal('hide');
                        $("#knowledge .modal-body").children().remove();
                    })

                    $('#knowledge').on('hidden.bs.modal', () => {
                        $("#knowledge .modal-body").children().remove();
                    })
                })


                $(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index} #add-group-${lessonNo}-${index}`).click(function() {
                    if (outlineDataArr[lessonNo].homework_question[index].content.options.length-1 == 3) {
                        alert("连线题不能超过四组连线");
                    } else {
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[index].content.options.push({
                            "head": "", 
                            "headImage": "", 
                            "tail": "", 
                            "tailImage": ""
                        });
                        // outlineDataArr[lessonNo].homework_question[index].other_group_number++;
                        renderMakeSubjects();
                    }
                })

                $($(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index}  .option-${lessonNo}-${index}-0 input[type=file]`)[0]).change(async function (e) {
                    let image = await uploadImageAndUpdateData(e.target.files[0]);
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[index].content.options[0].headImage = image;
                    renderMakeSubjects();
                })

                $(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index} #delete-image-${lessonNo}-${index}-0-0`).click(async function (e) {
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[index].content.options[0].headImage = '';
                    renderMakeSubjects();
                })

                $($(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index}  .option-${lessonNo}-${index}-0 input[type=file]`)[1]).change(async function (e) {
                    let image = await uploadImageAndUpdateData(e.target.files[0]);
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[index].content.options[0].tailImage = image;
                    renderMakeSubjects();
                })

                $(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index} #delete-image-${lessonNo}-${index}-0-1`).click(async function (e) {
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[index].content.options[0].tailImage = '';
                    renderMakeSubjects();
                })

                for (let id = 0; id < outlineDataArr[lessonNo].homework_question[index].content.options.length-1; id++) {
                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index} #delete-group-${lessonNo}-${index}-${id+2}`).click(function() {
                        if (outlineDataArr[lessonNo].homework_question[index].other_group_number == 1) {
                            alert("连线题至少有两组连线");
                        } else {
                            readAllValue();
                            outlineDataArr[lessonNo].homework_question[index].content.options.splice(id+2, 1);
                            // outlineDataArr[lessonNo].homework_question[index].other_group_number--;
                            renderMakeSubjects();
                        }
                    })

                    $($(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index}  .option-${lessonNo}-${index}-${id+1} input[type=file]`)[0]).change(async function (e) {
                        let image = await uploadImageAndUpdateData(e.target.files[0]);
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[index].content.options[id+1].headImage = image;
                        renderMakeSubjects();
                    })

                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index} #delete-image-${lessonNo}-${index}-${id+1}-0`).click(function (e) {
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[index].content.options[id+1].headImage = '';
                        renderMakeSubjects();
                    })
    
                    $($(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index}  .option-${lessonNo}-${index}-${id+1} input[type=file]`)[1]).change(async function (e) {
                        let image = await uploadImageAndUpdateData(e.target.files[0]);
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[index].content.options[id+1].tailImage = image;
                        renderMakeSubjects();
                    })

                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .connection-subject-body-${index} #delete-image-${lessonNo}-${index}-${id+1}-1`).click(async function (e) {
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[index].content.options[id+1].tailImage = '';
                        renderMakeSubjects();
                    })
                }
            }
        } else if (outlineDataArr[lessonNo].type == 4) {
            for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {

                // 知识点设置
                $(`.choice-subject-${outlineDataArr[lessonNo].id} #knowledge-${lessonNo}-${index}-4`).click(function() {
                    $(this).siblings("button.hidden").trigger("click");
                    $('#knowledge .modal-body').append(knowledgeDomStr(4));
                    $('#knowledge .modal-body .content').append(examination());

                    $("#save-knowledge").click(function() {
                        outlineDataArr[lessonNo].homework_question[index].content['knowledge_point_id'] = $('#knowledge option:selected').val();
                        outlineDataArr[lessonNo].homework_question[index].content['knowledge_point_remark'] = $('#knowledge input').val();
                        $('#knowledge').modal('hide');
                        $("#knowledge .modal-body").children().remove();
                    })

                    $('#knowledge').on('hidden.bs.modal', () => {
                        $("#knowledge .modal-body").children().remove();
                    })
                })


                $(`.choice-subject-${outlineDataArr[lessonNo].id} .sort-subject-body-${index} #add-sentence-${lessonNo}-${index}`).click(function() {
                    readAllValue();
                    outlineDataArr[lessonNo].homework_question[index].content.options.push({
                        "word": ""
                    });
                    renderMakeSubjects();
                })

                for (let id = 0; id < outlineDataArr[lessonNo].homework_question[index].content.options.length; id++) {
                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .sort-subject-body-${index} #delete-sentence-${lessonNo}-${index}-${id}`).click(function() {
                        readAllValue();
                        outlineDataArr[lessonNo].homework_question[index].content.options.splice(id, 1);
                        renderMakeSubjects();
                    })
                }
            }
        } else if (outlineDataArr[lessonNo].type == 5) {
            for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {// 每道阅读题
                let chioceSubjectNumber = 0, completionSubjectNumber = 0;
                outlineDataArr[lessonNo].homework_question[index].children.forEach((item, index) => {
                    if (item.type == 1) {
                        chioceSubjectNumber = item.homework_question.length;
                    } else if (item.type == 2) {
                        completionSubjectNumber = item.homework_question.length;
                    }
                })

                // 知识点设置
                $(`.choice-subject-${outlineDataArr[lessonNo].id} #knowledge-${lessonNo}-${index}-5`).click(function() {
                    $(this).siblings("button.hidden").trigger("click");
                    $('#knowledge .modal-body').append(knowledgeDomStr(5));
                    $('#knowledge .modal-body .content').append(examination());

                    $("#save-knowledge").click(function() {
                        outlineDataArr[lessonNo].homework_question[index]['knowledge_point_id'] = $('#knowledge option:selected').val();
                        outlineDataArr[lessonNo].homework_question[index]['knowledge_point_remark'] = $('#knowledge input').val();
                        $('#knowledge').modal('hide');
                        $("#knowledge .modal-body").children().remove();
                    })

                    $('#knowledge').on('hidden.bs.modal', () => {
                        $("#knowledge .modal-body").children().remove();
                    })
                })

                if (outlineDataArr[lessonNo].homework_question[index].children != null) {
                    for (let id = 0; id < outlineDataArr[lessonNo].homework_question[index].children.length; id++) {// 阅读题下的每道小题
                        let thisSmallSubject = outlineDataArr[lessonNo].homework_question[index].children[id];
    
                        $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} #edit-title-${lessonNo}-${thisSmallSubject.type}-${index}-${id}`).click(function() {
                            // 显示弹框
                            $("#exampleModal .modal-body").append(changeTitleInfo(thisSmallSubject.type, thisSmallSubject.name, thisSmallSubject.remark, thisSmallSubject.type == 1? chioceSubjectNumber : completionSubjectNumber, false))
                            $(this).siblings(`button.change-outline`).trigger("click");
    
                            // 保存修改的大纲
                            $(".sava-change").click(async function() {
                                let num = Number($("#exampleModal input[type=number]").val());
                                // 改变阅读题中一种题目类型的小题数目
                                if (num <= 0) {
                                    let result = await deleteOutline(thisSmallSubject.id);
                                    if (result == 'err') {
                                        alert('操作失败');
                                        return;
                                    }
                                    outlineDataArr[lessonNo].homework_question[index].children.splice(id, 1);
                                    readAllValue();
                                } else {
                                    let subjectLength = thisSmallSubject.homework_question.length;
                                    if ( subjectLength > num) {
                                        for (let i = subjectLength-1; i > num-1; i--) {
                                            let lastSubject = thisSmallSubject.homework_question[i];
                                            if (lastSubject.id) {
                                                let result = await deleteSmallSubject(lastSubject.id);
                                                if (result == 'err') {
                                                    alert('操作失败');
                                                    return;
                                                }
                                            }
                                            thisSmallSubject.homework_question.pop()
                                        }
                                        readAllValue();
                                    } else {
                                        readAllValue();
                                        // 增加这道大题的小题数量
                                        for (let i = thisSmallSubject.homework_question.length; i < num; i++) {
                                            let obj = {};
                                            obj['content'] = JSON.parse(JSON.stringify(typeToData[thisSmallSubject.type]));
                                            thisSmallSubject.homework_question.push(obj);
                                        }
                                    }
                                }
    
                                // 改变大纲题目name remark              
                                thisSmallSubject['name'] = $(".change-headerline-input").val();
                                thisSmallSubject['remark'] = $(".change-description-input").val();

                                $('#exampleModal').modal('hide');
                                $("#exampleModal .modal-body").children().remove();

                                readAllValue();
                                removeEventListener();
                                renderMakeSubjects();
                            })
    
                            $('#exampleModal').on('hidden.bs.modal', () => {
                                $("#exampleModal .modal-body").children().remove();
                                $(".sava-change").unbind();
                            })
                        })
    
                        $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} #delete-sort-${lessonNo}-${thisSmallSubject.type}-${index}-${id}`).click(function() {
                            readAllValue();
                            outlineDataArr[lessonNo].homework_question[index].children.splice(id, 1);
                            if (outlineDataArr[lessonNo].homework_question[index].children.length == 0) {
                                outlineDataArr[lessonNo].homework_question.splice(index, 1);
    
                                if (outlineDataArr[lessonNo].homework_question.length == 0) {
                                    outlineDataArr.splice(lessonNo, 1)
                                }
                            }
                            renderMakeSubjects();
                        })
    
                        if (thisSmallSubject.type == 1) {
    
                            thisSmallSubject.homework_question.forEach((item, i) => {

                                $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} #add-other-option-${lessonNo}-${index}-1-${i}`).click(function() {
                                    if (thisSmallSubject.homework_question[i].content.options.length == 6) {
                                        alert("选择题选项为2-6个")
                                    } else {
                                        readAllValue();
                                        thisSmallSubject.homework_question[i].content.options.push({
                                            "answer": "", 
                                            "answerImage": ""
                                        });
                                        renderMakeSubjects();
                                    }
                                })
    
                                $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} .option-stem-${i} input[type=file]`).change(async function (e) {
                                    let image = await uploadImageAndUpdateData(e.target.files[0]);
                                    readAllValue();
                                    thisSmallSubject.homework_question[i].content.questionImage = image;
                                    renderMakeSubjects();
                                })
    
                                $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} #delete-stem-image-${lessonNo}-${index}-${i}`).click(async function (e) {
                                    readAllValue();
                                    thisSmallSubject.homework_question[i].content.questionImage = '';
                                    renderMakeSubjects();
                                })
    
                                $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} .right-option input[type=file]`).change(async function (e) {
                                    let image = await uploadImageAndUpdateData(e.target.files[0]);
                                    readAllValue();
                                    thisSmallSubject.homework_question[i].content.options[0].answerImage = image;
                                    renderMakeSubjects();
                                })
    
                                $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} #delete-right-image-${lessonNo}-${index}-${i}`).click(async function (e) {
                                    readAllValue();
                                    thisSmallSubject.homework_question[i].content.options[0].answerImage = '';
                                    renderMakeSubjects();
                                })
    
                                $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} .first-other-option-${i} input[type=file]`).change(async function (e) {
                                    let image = await uploadImageAndUpdateData(e.target.files[0]);
                                    readAllValue();
                                    thisSmallSubject.homework_question[i].content.options[1].answerImage = image;
                                    renderMakeSubjects();
                                })
    
                                $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} #delete-other-image-${lessonNo}-${index}-1-${i}`).click(async function (e) {
                                    readAllValue();
                                    thisSmallSubject.homework_question[i].content.options[1].answerImage = '';
                                    renderMakeSubjects();
                                })
                                
                                for (let ii = 2; ii < thisSmallSubject.homework_question[i].content.options.length; ii++) {
                                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} #delete-option-${lessonNo}-${index}-${id}-${i}-${ii}`).click(function() {
                                        readAllValue();
                                        thisSmallSubject.homework_question[i].content.options.splice(ii, 1);
                                        renderMakeSubjects();
                                    })
    
                                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} .other-option-${id}-${i}-${ii} input[type=file]`).change(async function (e) {
                                        let image = await uploadImageAndUpdateData(e.target.files[0]);
                                        readAllValue();
                                        thisSmallSubject.homework_question[i].content.options[ii].answerImage = image;
                                        renderMakeSubjects();
                                    })
    
                                    $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .choice-subject-body-${lessonNo}-1-${i} #delete-other-image-${lessonNo}-${index}-${id}-${i}-${ii}`).click(async function (e) {
                                        readAllValue();
                                        thisSmallSubject.homework_question[i].content.options[ii].answerImage = '';
                                        renderMakeSubjects();
                                    })
                                }
                            })
                        } else {
                            thisSmallSubject.homework_question.forEach((item, i) => {
                                $(`.choice-subject-${outlineDataArr[lessonNo].id} .richtext-${lessonNo}-${index} .completion-sunject-body-${lessonNo}-${id}-${i} #add-complete-${lessonNo}-${index}-${id}-${i}-${thisSmallSubject.type}`).click(function() {
                                    readAllValue();
                                    thisSmallSubject.homework_question[i].content.options = thisSmallSubject.homework_question[i].content.options.concat(JSON.parse(JSON.stringify(typeToData[2].options)));
                                    renderMakeSubjects();
                                })
                            })
                        }
                    }
                }
            }
        } else if (outlineDataArr[lessonNo].type == 6) {
            $(`.choice-subject-${outlineDataArr[lessonNo].id} input`).change(async function (e) {
                let type;
                if (e.target.files[0].type == 'application/pdf') {
                    type = 3;
                } else {
                    type = 2;
                }
                let result = await uploadImage(e.target.files[0]);
                readAllValue()
                outlineDataArr[lessonNo].homework_question[0].content['fileUrl'] = result;
                outlineDataArr[lessonNo].homework_question[0].content['fileType'] = type;
                renderMakeSubjects()
            })

            $("#delete-other-file").click(function() {
                readAllValue();
                outlineDataArr[lessonNo].homework_question[0].content['fileUrl'] = null;
                outlineDataArr[lessonNo].homework_question[0].content['fileType'] = null;
                renderMakeSubjects();
            })
        }
    }
}

// 读取选择题输入值
function readChoiceQuestionValues(lessonNo, subjectItem) {
    for (let index = 0; index < subjectItem.homework_question.length; index++) {
        let thisSmallSubject = subjectItem.homework_question[index];
        thisSmallSubject.content.question = $.trim($(`.choice-subject-${subjectItem.id} .choice-subject-body-${index} #stem-${index}-${lessonNo}`).val());
        // outlineDataArr[lessonNo].homework_question.content['questionImage'] = $(`.choice-subject-${lessonNo} .choice-subject-body-${i} #upload-image`).val();
        thisSmallSubject.content.options[0].answer = $.trim($(`.choice-subject-${subjectItem.id} .choice-subject-body-${index} .right-option #right-option-stem-${index}-${lessonNo}`).val());
        thisSmallSubject.content.options[1].answer = $.trim($(`.choice-subject-${subjectItem.id} .choice-subject-body-${index} .first-other-option #other-option-stem-${index}-${lessonNo}`).val());

        for (let id = 2; id < thisSmallSubject.content.options.length; id++) {
            thisSmallSubject.content.options[id].answer = $.trim($(`.choice-subject-${subjectItem.id} .choice-subject-body-${index} .other-option-bag #other-option-text-${id}-${lessonNo}-${index}`).val());
        }
    }
}

// 读取填空题输入值
function readCompletionQuestionValues(lessonNo, subjectItem) {
    for (let index = 0; index < subjectItem.homework_question.length; index++) {
        let thisSmallSubject = subjectItem.homework_question[index];

        // 读每组前句后句值
        for (let id = 0; id < thisSmallSubject.content.options.length/3; id++) {
            thisSmallSubject.content.options[id*3].sentence = $.trim($(`.choice-subject-${subjectItem.id} .completion-sunject-body-${index} #font-${lessonNo}-${index}-${id*3}`).val());
            thisSmallSubject.content.options[id*3+1].sentence = $.trim($(`.choice-subject-${subjectItem.id} .completion-sunject-body-${index} #right-answer-${lessonNo}-${index}-${id*3+1}`).val());
            thisSmallSubject.content.options[id*3+2].sentence = $.trim($(`.choice-subject-${subjectItem.id} .completion-sunject-body-${index} #end-${lessonNo}-${index}-${id*3+2}`).val());
        }
    }
}

// 读取连线题输入值
function readConnectionQuestionValues(lessonNo, subjectItem) {
    for (let index = 0; index < subjectItem.homework_question.length; index++) {
        let thisSmallSubject = subjectItem.homework_question[index];

        thisSmallSubject.content.options[0].head = $.trim($(`.choice-subject-${subjectItem.id} .connection-subject-body-${index} #stem-${lessonNo}-${index}-0`).val());
        thisSmallSubject.content.options[0].tail = $.trim($(`.choice-subject-${subjectItem.id} .connection-subject-body-${index} #answer-${lessonNo}-${index}-0`).val());
        // 读其他组连线值
        for (let id = 0; id < thisSmallSubject.content.options.length-1; id++) {
            thisSmallSubject.content.options[id+1].head = $.trim($(`.choice-subject-${subjectItem.id} .connection-subject-body-${index} #stem-${lessonNo}-${index}-${id+1}`).val());
            thisSmallSubject.content.options[id+1].tail = $.trim($(`.choice-subject-${subjectItem.id} .connection-subject-body-${index} #answer-${lessonNo}-${index}-${id+1}`).val());
        }
    }
}

// 读取排序题输入内容
function readSortQuestionValues(lessonNo, subjectItem) {
    for (let index = 0; index < subjectItem.homework_question.length; index++) {
        let thisSmallSubject = subjectItem.homework_question[index];

        thisSmallSubject.content.pre = $.trim($(`.choice-subject-${subjectItem.id} .sort-subject-body-${index} #pre-sentence-${lessonNo}-${index}`).val());
        thisSmallSubject.content.post = $.trim($(`.choice-subject-${subjectItem.id} .sort-subject-body-${index} #post-sentence-stem-${lessonNo}-${index}`).val());

        for (let id = 0; id < thisSmallSubject.content.options.length; id++) {
            thisSmallSubject.content.options[id].word = $.trim($(`.choice-subject-${subjectItem.id} .sort-subject-body-${index} #other-sort-stem-${lessonNo}-${index}-${id}`).val());
        }
    }
}

// 读取阅读题输入内容
function readReadQuestionValues(lessonNo, subjectItem) {
    for (let index = 0; index < subjectItem.homework_question.length; index++) {
        let thisSmallSubject = subjectItem.homework_question[index];
        thisSmallSubject.content = editorList[`${subjectItem.id}-${index}`].txt.html();

        if (thisSmallSubject.children != null) {
            for (let id = 0; id < thisSmallSubject.children.length; id++) {
                let everySmallSubject = thisSmallSubject.children[id];
                everySmallSubject.homework_question.forEach((item, i) => {
                    let chioceSubject = item;
    
                    if (everySmallSubject.type == 1) {
                        chioceSubject.content.question = $.trim($(`.choice-subject-${subjectItem.id} #stem-${lessonNo}-${index}-1-${i}`).val());
                        chioceSubject.content.options[0].answer = $.trim($(`.choice-subject-${subjectItem.id} #right-option-stem-${lessonNo}-${index}-1-${i}`).val());
                        chioceSubject.content.options[1].answer = $.trim($(`.choice-subject-${subjectItem.id} #other-option-stem-${lessonNo}-${index}-1-${i}`).val());
        
                        for (let ii = 2; ii < chioceSubject.content.options.length; ii++) {
                            chioceSubject.content.options[ii].answer = $.trim($(`.choice-subject-${subjectItem.id} #other-option-text-${lessonNo}-${index}-${id}-${i}-${ii}`).val());
                        }
                    } else {
                        for (let ii = 0; ii < chioceSubject.content.options.length/3; ii++) {
                            chioceSubject.content.options[ii*3].sentence = $.trim($(`.choice-subject-${subjectItem.id} .completion-sunject-body-${lessonNo}-${id}-${i} #font-${lessonNo}-${index}-${id*3}-${i}-${ii}`).val());
                            chioceSubject.content.options[ii*3+1].sentence = $.trim($(`.choice-subject-${subjectItem.id} .completion-sunject-body-${lessonNo}-${id}-${i} #right-answer-${lessonNo}-${index}-${id*3+1}-${i}-${ii}`).val());
                            chioceSubject.content.options[ii*3+2].sentence = $.trim($(`.choice-subject-${subjectItem.id} .completion-sunject-body-${lessonNo}-${id}-${i} #end-${lessonNo}-${index}-${id*3+2}-${i}-${ii}`).val());
                        }
                    }
                })
            }
        }
    }
}

// 读取所有已经填过的内容
function readAllValue() {
    for (let lessonNo in outlineDataArr) {
        switch(outlineDataArr[lessonNo].type) {
            case 1:
               readChoiceQuestionValues(lessonNo, outlineDataArr[lessonNo])
               break;
            case 2:
                readCompletionQuestionValues(lessonNo, outlineDataArr[lessonNo])
                break;
            case 3:
                readConnectionQuestionValues(lessonNo, outlineDataArr[lessonNo])
                break;
            case 4:
                readSortQuestionValues(lessonNo, outlineDataArr[lessonNo])
                break;
            case 5:
                readReadQuestionValues(lessonNo, outlineDataArr[lessonNo])
                break;
        }
    }
}

// 渲染制作题目页面
function renderMakeSubjects() {
    console.log(outlineDataArr)

    $(".homework-detail-content section").remove();
    for (let lessonNo in outlineDataArr) {
        let subjectId = outlineDataArr[lessonNo].id;

        $(".homework-detail-content").append(section(subjectId));
        $(`.choice-subject-${subjectId}`).append(sortTitleDomStr(outlineDataArr[lessonNo].type, lessonNo, outlineDataArr[lessonNo].name, outlineDataArr[lessonNo].remark));

        // 需要一个状态判断怎么渲染题目
        if (outlineDataArr[lessonNo].homework_question.length > 0) { 
            if (outlineDataArr[lessonNo].type == 1) {
                for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {
                    let content = outlineDataArr[lessonNo].homework_question[index].content;
                    $(`.choice-subject-${subjectId}`).append(choiceQuestionsDomStr(index, outlineDataArr[lessonNo].type, content.question, content.questionImage, content.options[0].answer, content.options[0].answerImage, content.options[1].answer, content.options[1].answerImage, lessonNo, true));
    
                    // 选择题
                    for (let id = 2; id < content.options.length; id++) {
                        $(`.choice-subject-${subjectId} .choice-subject-body-${index} .other-option-bag`).append(otherOption(lessonNo, index, id, content.options[id].answer, content.options[id].answerImage))
                    }
                }
            } else if (outlineDataArr[lessonNo].type == 2) {
                for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {
                    let content = outlineDataArr[lessonNo].homework_question[index].content;

                    $(`.choice-subject-${subjectId}`).append(completionSubjectBodyDiv(index))
                    for (let id = 0; id < content.options.length/3; id++) {
                        if (id == 0) {
                            $(`.choice-subject-${subjectId} .completion-sunject-body-${index}`).append(oneGroupBaseCompletion(lessonNo, index, id, outlineDataArr[lessonNo].type, content.options[3*id].sentence, content.options[3*id+1].sentence, content.options[3*id+2].sentence));
                        } else {
                            $(`.choice-subject-${subjectId} .completion-sunject-body-${index}`).append(oneGroupCompletion(lessonNo, index, id, content.options[3*id].sentence, content.options[3*id+1].sentence, content.options[3*id+2].sentence));
                        }
                    }
                    $(`.choice-subject-${subjectId} .completion-sunject-body-${index}`).append(completeAddOtherOptionBtn(lessonNo, index));
                }
            } else if (outlineDataArr[lessonNo].type == 3) {
                for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {
                    let content = outlineDataArr[lessonNo].homework_question[index].content,
                        isShowAddBtn = content.options.length == 1;

                    $(`.choice-subject-${subjectId}`).append(connectionBaseGroup(lessonNo, index, outlineDataArr[lessonNo].type, content.options[0].head, content.options[0].headImage, content.options[0].tail, content.options[0].tailImage, isShowAddBtn));
                    for (let id = 0; id < content.options.length-1; id++) {
                        $(`.choice-subject-${subjectId} .connection-subject-body-${index}`).append(connectionOtherGroup(lessonNo, index, id+1, content.options[id+1].head, content.options[id+1].headImage, content.options[id+1].tail, content.options[id+1].tailImage, id==(content.options.length-2)?true: false))
                    }
                }
            } else if (outlineDataArr[lessonNo].type == 4) {
                for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {
                    let content = outlineDataArr[lessonNo].homework_question[index].content;
                        


                    $(`.choice-subject-${subjectId}`).append(sortBaseSubject(lessonNo, index, outlineDataArr[lessonNo].type, content.pre, content.post));
                    for (let id = 0; id < content.options.length; id++) {
                        $(`.choice-subject-${subjectId} .sort-subject-body-${index}`).append(sortOtherItem(lessonNo, index, id, sortObj[id], content.options[id].word, id!=0&&id!=content.options.length-1, id==content.options.length-1&&id!=3))
                    }
                }
            } else if (outlineDataArr[lessonNo].type == 5) {
                for (let index = 0; index < outlineDataArr[lessonNo].homework_question.length; index++) {
                    $(`.choice-subject-${subjectId}`).append(richTextBaseItem(lessonNo, index, outlineDataArr[lessonNo].type));
                    let E = window.wangEditor
                    let editor = new E(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index} .article`)
                    editor.create()
                    editor.txt.html(outlineDataArr[lessonNo].homework_question[index].content);
                    editorList[`${outlineDataArr[lessonNo].id}-${index}`] = editor;

                    $(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index}`).append(`<div class='pt20 richtext-subjects-${lessonNo}-${index}'></div>`);

                    if (outlineDataArr[lessonNo].homework_question[index].children != null) {
                        for (let id = 0; id < outlineDataArr[lessonNo].homework_question[index].children.length; id++) {// 循环阅读题的所有小题

                            let thisSmallSubject = outlineDataArr[lessonNo].homework_question[index].children[id]; // 阅读题里边的小题，默认一套选择题，一套填空题
                            $(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index} .richtext-subjects-${lessonNo}-${index}`).append(sortTitleDomStrInReadQuestion(thisSmallSubject.type, lessonNo, index, id, thisSmallSubject.name, thisSmallSubject.remark));
    
                            if (thisSmallSubject.type == 1) {// 选择题
                                thisSmallSubject.homework_question.forEach((item, i) => {
                                    $(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index} .richtext-subjects-${lessonNo}-${index}`).append(choiceQuestionsInReadQuestionDomStr(lessonNo, index, i, thisSmallSubject.type, item.content.question, item.content.questionImage, item.content.options[0].answer, item.content.options[0].answerImage, item.content.options[1].answer, item.content.options[1].answerImage));
                                    for (let ii = 2; ii < item.content.options.length; ii++) {
                                        $(`.choice-subject-${subjectId} .choice-subject-body-${lessonNo}-${thisSmallSubject.type}-${i} .other-option-bag`).append(otherOptionInReadQuestion(lessonNo, index, id, i, ii, item.content.options[ii].answer, item.content.options[ii].answerImage))
                                    }

                                })
                            } else if (thisSmallSubject.type == 2) {// 填空题
                                thisSmallSubject.homework_question.forEach((item, i) => {
                                    $(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index} .richtext-subjects-${lessonNo}-${index}`).append(completionSubjectBodyDivInReadQuestion(lessonNo, id, i));
        
                                    for (let ii = 0; ii < item.content.options.length/3; ii++) {// 填空题第几组前句后句
                                        if (ii == 0) {
                                            $(`.choice-subject-${subjectId} .completion-sunject-body-${lessonNo}-${id}-${i}`).append(oneGroupBaseCompletionInReadQuestion(lessonNo, index, id, i, ii, thisSmallSubject.type, item.content.options[3*ii].sentence, item.content.options[3*ii+1].sentence, item.content.options[3*ii+2].sentence));
                                        } else {
                                            $(`.choice-subject-${subjectId} .completion-sunject-body-${lessonNo}-${id}-${i}`).append(oneGroupCompletionInReadQuestion(lessonNo, index, id, i, ii, item.content.options[3*ii].sentence, item.content.options[3*ii+1].sentence, item.content.options[3*ii+2].sentence));
                                        }
                                    }
                                    $(`.choice-subject-${subjectId} .completion-sunject-body-${lessonNo}-${id}-${i}`).append(completeAddOtherOptionBtnInReadQuestion(lessonNo, index, id, i, 2));
                                })            
                            }
                        }
                    }
                }
            } else if (outlineDataArr[lessonNo].type == 6) {
                if (outlineDataArr[lessonNo].homework_question[0].content.fileType == 2) {
                    // $(`.choice-subject-${subjectId}`).append(`<div class='pl20 mb20'><img src="${outlineDataArr[lessonNo].homework_question[0].content.fileUrl}"></div>`);
                    $(`.choice-subject-${subjectId}`).append(`<div class='pl20 mb20'><img src="${outlineDataArr[lessonNo].homework_question[0].content.fileUrl}"><div><button id="delete-other-file">删除文件</button></div></div>`);
                } else if (outlineDataArr[lessonNo].homework_question[0].content.fileType == 3) {
                    // $(`.choice-subject-${subjectId}`).append(`<div class='pl20'><iframe src="${outlineDataArr[lessonNo].homework_question[0].content.fileUrl}" frameborder="0" style="width: 100%; height: 500px"></iframe></div>`);
                    $(`.choice-subject-${subjectId}`).append(`<div class='pl20'><iframe src="${outlineDataArr[lessonNo].homework_question[0].content.fileUrl}" frameborder="0" style="width: 100%; height: 500px"></iframe><div><button id="delete-other-file">删除文件</button></div></div>`);
                } else {
                    $(`.choice-subject-${subjectId}`).append("<div class='pl20'><input type='file' accept='image/*, application/pdf'></div>");
                }
            }
        } else { //重新编辑
            // 这道大题的小题数量
            for (let index = 0; index < outlineDataArr[lessonNo].quality; index++) {
                // $(`.choice-subject-${subjectId}`).append(choiceQuestionsDomStr(index, null, null, null, null, null, null));
                
                if (outlineDataArr[lessonNo].type == 1) { // 这道小题是选择题时，初始其他选项数量和其他数据
                    $(`.choice-subject-${subjectId}`).append(choiceQuestionsDomStr(index, outlineDataArr[lessonNo].type, null, null, null, null, null, null, lessonNo, true));
                    outlineDataArr[lessonNo]['homework_question'][index] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['other_option_quality'] = 3;
                    outlineDataArr[lessonNo]['homework_question'][index]['content'] = JSON.parse((JSON.stringify(typeToData[1])));

                    for (let id = 2; id < 4; id++) {
                        $(`.choice-subject-${subjectId} .choice-subject-body-${index} .other-option-bag`).append(otherOption(lessonNo, index, id, null, null))
                    }
                } else if (outlineDataArr[lessonNo].type == 2) {
                    $(`.choice-subject-${subjectId}`).append(completionSubjectBodyDiv(index));

                    outlineDataArr[lessonNo]['homework_question'][index] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['group_number'] = 1;
                    outlineDataArr[lessonNo]['homework_question'][index]['content'] = JSON.parse((JSON.stringify(typeToData[2])));
                    for (let id = 0; id < outlineDataArr[lessonNo]['homework_question'][index]['content'].options.length/3; id++) {
                        if (id == 0) {
                            $(`.choice-subject-${subjectId} .completion-sunject-body-${index}`).append(oneGroupBaseCompletion(lessonNo, index, id, outlineDataArr[lessonNo].type, null, null, null));
                        } else {
                            $(`.choice-subject-${subjectId} .completion-sunject-body-${index}`).append(oneGroupCompletion(lessonNo, index, id, null, null, null));
                        }
                    }
                    $(`.choice-subject-${subjectId} .completion-sunject-body-${index}`).append(completeAddOtherOptionBtn(lessonNo, index));
                } else if (outlineDataArr[lessonNo].type == 3) {
                    $(`.choice-subject-${subjectId}`).append(connectionBaseGroup(lessonNo, index, outlineDataArr[lessonNo].type, null, null, null, null));

                    outlineDataArr[lessonNo]['homework_question'][index] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['other_group_number'] = 3;
                    outlineDataArr[lessonNo]['homework_question'][index]['content'] = JSON.parse((JSON.stringify(typeToData[3])));

                    for (let id = 0; id < outlineDataArr[lessonNo].homework_question[index].other_group_number; id++) {
                        $(`.choice-subject-${subjectId} .connection-subject-body-${index}`).append(connectionOtherGroup(lessonNo, index, id+1, null, null, null, null, (id==(outlineDataArr[lessonNo].homework_question[index].other_group_number-1))?true:false))
                    }
                } else if (outlineDataArr[lessonNo].type == 4) {
                    $(`.choice-subject-${subjectId}`).append(sortBaseSubject(lessonNo, index, outlineDataArr[lessonNo].type, null, null));

                    outlineDataArr[lessonNo]['homework_question'][index] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['sort_number'] = 4;
                    outlineDataArr[lessonNo]['homework_question'][index]['content'] = JSON.parse((JSON.stringify(typeToData[4])));

                    for (let id = 0; id < outlineDataArr[lessonNo]['homework_question'][index]['sort_number']; id++) {
                        $(`.choice-subject-${subjectId} .sort-subject-body-${index}`).append(sortOtherItem(lessonNo, index, id, sortObj[id], null, id!=0&&id!=outlineDataArr[lessonNo]['homework_question'][index]['sort_number'].length-1))
                    }
                } else if (outlineDataArr[lessonNo].type == 5) {
                    $(`.choice-subject-${subjectId}`).append(richTextBaseItem(lessonNo, index, outlineDataArr[lessonNo].type));

                    let E = window.wangEditor
                    let editor = new E(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index} .article`)
                    editor.create()
                    editorList[`${outlineDataArr[lessonNo].id}-${index}`] = editor;

                    outlineDataArr[lessonNo]['homework_question'][index] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['content'] = null;
                    outlineDataArr[lessonNo]['homework_question'][index]['children'] = [];
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][0] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][0]['type'] = 1;
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][0]['name'] = typeToheaderlineAndDescription[1].headerline;
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][0]['remark'] = typeToheaderlineAndDescription[1].description;
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][0]['homework_question'] = [];
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][0]['homework_question'][0] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][0]['homework_question'][0].content = JSON.parse(JSON.stringify(typeToData[1]));
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][1] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][1]['type'] = 2;
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][1]['name'] = typeToheaderlineAndDescription[2].headerline;
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][1]['remark'] = typeToheaderlineAndDescription[2].description;
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][1]['homework_question'] = [];
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][1]['homework_question'][0] = {};
                    outlineDataArr[lessonNo]['homework_question'][index]['children'][1]['homework_question'][0].content = JSON.parse(JSON.stringify(typeToData[2]));
                    
                    $(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index}`).append(`<div class='pt20 richtext-subjects-${lessonNo}-${index}'></div>`);

                    for (let id = 0; id < outlineDataArr[lessonNo].homework_question[index].children.length; id++) {// 循环阅读题的所有小题

                        let thisSmallSubject = outlineDataArr[lessonNo].homework_question[index].children[id]; // 阅读题里边的小题，默认一道选择题，一道填空题
                        $(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index} .richtext-subjects-${lessonNo}-${index}`).append(sortTitleDomStrInReadQuestion(thisSmallSubject.type, lessonNo, index, id, null, null));

                        if (thisSmallSubject.type == 1) {// 选择题

                            let thisSubject = thisSmallSubject.homework_question[0].content;
                            $(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index} .richtext-subjects-${lessonNo}-${index}`).append(choiceQuestionsInReadQuestionDomStr(lessonNo, index, 0, thisSmallSubject.type, thisSubject.question, thisSubject.questionImage, thisSubject.options[0].answer, thisSubject.options[0].answerImage, thisSubject.options[1].answer, thisSubject.options[1].answerImage));

                            for (let i = 2; i < 4; i++) {
                                $(`.choice-subject-${subjectId} .choice-subject-body-${lessonNo}-${thisSmallSubject.type}-0 .other-option-bag`).append(otherOptionInReadQuestion(lessonNo, index, id, 0, i, null, null))
                            }
        
                        } else if (thisSmallSubject.type == 2) {// 填空题
                            let thisSubject = thisSmallSubject.homework_question[0].content;
                            $(`.choice-subject-${subjectId} .richtext-${lessonNo}-${index} .richtext-subjects-${lessonNo}-${index}`).append(completionSubjectBodyDivInReadQuestion(lessonNo, id, 0));

                            for (let i = 0; i < thisSubject.options.length/3; i++) {// 填空题第几组前句后句
                                if (i == 0) {
                                    $(`.choice-subject-${subjectId} .completion-sunject-body-${lessonNo}-${id}-${i}`).append(oneGroupBaseCompletionInReadQuestion(lessonNo, index, id, 0, i, thisSmallSubject.type, thisSubject.options[3*i].sentence, thisSubject.options[3*i+1].sentence, thisSubject.options[3*i+2].sentence));
                                } else {
                                    $(`.choice-subject-${subjectId} .completion-sunject-body-${lessonNo}-${id}-${i}`).append(oneGroupCompletionInReadQuestion(lessonNo, index, id, 0, i, thisSubject.options[3*id].sentence, thisSubject.options[3*id+1].sentence, thisSubject.options[3*id+2].sentence));
                                }
                            }
                            $(`.choice-subject-${subjectId} .completion-sunject-body-${lessonNo}-${index}-0`).append(completeAddOtherOptionBtnInReadQuestion(lessonNo, index, id, 0, 2));
        
                        }
                    }
                } else if (outlineDataArr[lessonNo].type == 6) {
                    $(`.choice-subject-${subjectId}`).append("<div class='pl20'><input type='file' accept='image/*, application/pdf'></div>");
                    outlineDataArr[lessonNo].homework_question.push({
                        content: {
                            fileUrl: null,
                            fileType: null
                        }
                    })
                }
                
            }
        }
    }
    
    // 渲染完成执行绑定事件
    bindingMakeSubjectsEvent();
}

// 开始loadin
function startLoading() {
    $('#loadingModal').modal({backdrop: 'static', keyboard: false});
}

// end loading
function endLoading() {
    $('#loadingModal').modal('hide');
}

// 这节课是否已经有作业
async function ifHasHomeworkThisClass() {
    $("#change-homework-subject").remove();
    hasUploadSubject = await hasSubject($("select.select-class").val())
    if (hasUploadSubject) {
        $(".homework-btns").append(`<button type="button" style="margin-right: 20px;" id="change-homework-subject">修改</button>`);
        // 点击修改
        $("#change-homework-subject").click(() => {
            let lessonId = $(".select-class option:selected").val();
            window.location.href=`/man/questions/?lessonId=${lessonId}&type=0`;
        })
    } 
}

//绑定事件
function bindingEvent() {

    $("#homework-page-preview").click(async function () {
        let result = await getOutline($(this).attr("data-lesson_id"), 1);
        if (result) {
            $(".preview").modal('show');
            $('.preview').on('hidden.bs.modal', function (e) {
                $('.preview .preview-page-container').children().remove()
            });
        }
    })

    if ($("select.select-class").val()) ifHasHomeworkThisClass();

    $("select.select-class").change(ifHasHomeworkThisClass)

    $("#new-outline").click(function() {
        renderSubjects(8);
        $("#newHomework").modal('show');
        $("#newHomework").on('hidden.bs.modal', function(e) {
            $("#newHomework .outline-content").children().remove();
            $(".jump-detail").unbind();
        })

        // 点击增加题目类型
        $(".modal-content > button").click(() => {
            if (defaultLessonSubjects == 20) {
                alert('您的题目过多')
            } else {
                $(".outline-content").append($(outlineSubjectDomStr(defaultLessonSubjects)));
                defaultLessonSubjects++;
            }
        })

        // 判断大纲题目数量是否是数字,不能大于20
        $(".subject-amount").change(function() {
            let num = $(this).val();
            if (!(!isNaN(num) && num % 1 === 0 && num > 0)) {
                alert("请输入大于0的整数数字");
                $(this).val("");
                $(this).focus();
            }
            if (num > 20) {
                alert("您的题目过多");
                $(this).val("");
                $(this).focus();
            }
        })

        $(".outline-content select").each(function (selectIndex) {
            $(this).change(function() {
                if ($(this).val() == 5 || $(this).val() == 6) {
                    if ($(this).val() == 5) {
                        if (hasReadQuestion) {
                            alert('只能有一道阅读题或其他题型');
                            $(this).find("option[value=5]").removeAttr("selected");
                            $($(this).siblings("input")).val('');
                            return;
                        } 
                    } else if ($(this).val() == 6) {
                        if (hasOtherQuestion) {
                            alert('只能有一道阅读题或其他题型');
                            $(this).find("option[value=6]").removeAttr("selected");
                            $($(this).siblings("input")).val('');
                            return;
                        }
                    }
                    $($(this).siblings("input"))
                    .val('1')
                    .attr("readonly", true)
                } else {
                    $($(this).siblings("input"))
                        .val('')
                        .removeAttr("readonly")
                }
                $(".outline-content select").each(function (select, selectItem) {
                    if ($(selectItem).find("option:selected").val() == 5) {
                        hasReadQuestion = true;
                    } else if ($(selectItem).find("option:selected").val() == 6) {
                        hasOtherQuestion = true;
                    }
                });
            })
        })

        // 点击提交大纲
        $(".jump-detail").click(async () => {
            if (isRequesting) return;
            if (hasUploadSubject) {
                let ifCover = await confirm("课程中已经有作业了，如果新建之后上传会覆盖原来的作业，是否确定新建？");
                if (!ifCover) {
                    $("#newHomework").modal('hide');
                    return;
                }
            } 
            var submitOutlineObj = {};
            let outlineSubjectArr = [],
                outlineAmountArr = [];

            for(let i = 0; i < defaultLessonSubjects; i++) {
                let formClass = `.form${i}`,
                    subject = $(`${formClass} #subject-${i} option:selected`).val(),
                    amount = $(`${formClass} input`).val();
                
                if (amount != 0) {
                    outlineSubjectArr.push(subject);
                    outlineAmountArr.push(amount);
                }
            }

            submitOutlineObj["lesson_id"] = $(".select-class option:selected").val();
            submitOutlineObj["outline_id"] = "1";
            submitOutlineObj["types"] = outlineSubjectArr;
            submitOutlineObj["qualitys"] = outlineAmountArr;

            isRequesting = true;
            let submitResult = await jqPromiseAjax({
                url: '/homework/outline_group/add_outlines/',
                type: 'post',
                data: JSON.stringify(submitOutlineObj)
            })
            if (submitResult.code == 0) {
                isRequesting = false;
                window.location.href=`/man/questions/?lessonId=${submitOutlineObj["lesson_id"]}&type=0`;
                
            }
        })
    })
    
    // 知识点大纲
    $("#save-outline-knowledge").click(async function() {
        let obj = {};
        obj['lesson_id'] = $(".select-class option:selected").val();
        obj['inspection_content'] = $("#knowledgePoint textarea").val();
        let result = await setKnowledgePoint(obj)
        if (result) {
            $("#knowledgePoint").modal('hide');
            alert('保存成功')
        }
    })

    // 点击预览
    $("#homework-preview-in-lessonpage").click(async function() {
        startLoading();
        let result = await getOutline($(".select-class option:selected").val(), 1);
        endLoading();
        if (result) {
            $(".preview").modal('show');
            $('.preview').on('hidden.bs.modal', function (e) {
                $('.preview .preview-page-container').children().remove()
            });
        }
    })


    // 点击发布
    $("#publish-homework-subject").click(async () => {
        if (isRequesting) return;
        isRequesting = true;
        let lessonId = $(".select-class option:selected").val();
        await publishHomework(lessonId);
        isRequesting = false;
    })

    // 老版本上传文件
    $("#old-edition-upload-homework").click(async function () {
        let files = $("#old-edition-upload-homework-input").prop('files'),
            lesson_id = $(".select-class option:selected").val();
        if (files.length == 0) {
            alert('请选择文件');
            return;
        }
        let formData = new FormData();
        formData.append('hw_content', files[0])
        formData.append('session', lesson_id)
        let result = await uploadFile(formData);
        if (result) {
            alert('上传成功');
        }
    })

}


function renderAndBindAdjustModal() {
    let isDeleting = false,
        hasReadQuestion = outlineDataArr.some((subject) => subject.type == 5),
        hasOtherQuestion = outlineDataArr.some((subject) => subject.type == 6);
    $('#adjustment .modal-body').children().remove();
    $(`#adjust-outline`).unbind();

    outlineDataArr.forEach((item, lessonNo) => {
        $('#adjustment .modal-body').append(adjustmentDomStr(lessonNo));

        if (item.id) {
            $(`.adjustment-${lessonNo}`).append(adjustSubjectItem(item.type, item.homework_question.length))
        } else {
            $(`.adjustment-${lessonNo}`).append(addAdjustSubjectItem(lessonNo, item.type))

            $(`.adjustment-${lessonNo} .select-${lessonNo}`).change(function() {
                outlineDataArr[lessonNo].type = $(`.adjustment-${lessonNo} .select-${lessonNo} option:selected`).val();
            })

            $(`.adjustment-${lessonNo} .input-${lessonNo}`).change(function() {
                outlineDataArr[lessonNo].quality = $(`.adjustment-${lessonNo} .input-${lessonNo}`).val();
            })

        }
        $(`.adjustment-${lessonNo}`).append(adjustmentBtns(lessonNo))

        $(`.adjustment-${lessonNo} .up-btn-${lessonNo}`).click(function() {
            if (lessonNo != 0) {
                outlineDataArr.splice(lessonNo-1, 0, outlineDataArr.splice(lessonNo, 1)[0]);
                renderAndBindAdjustModal();
            }
        })

        $(`.adjustment-${lessonNo} .down-btn-${lessonNo}`).click(function() {
            if (lessonNo != outlineDataArr.length-1) {
                outlineDataArr.splice(lessonNo+1, 0, outlineDataArr.splice(lessonNo, 1)[0]);
                renderAndBindAdjustModal();
            }
        })

        $(`.adjustment-${lessonNo} .add-btn-${lessonNo}`).click(function() {

            outlineDataArr.splice(lessonNo+1, 0, {id: null, type: null, quality: null});
            renderAndBindAdjustModal();
        })

        $(`.adjustment-${lessonNo} .delete-btn-${lessonNo}`).click(async function() {
            if (item.id == null) {
                outlineDataArr.splice(lessonNo, 1);
                renderAndBindAdjustModal();
                return;
            }
            if (isDeleting) return;
            isDeleting = true;
            let result = await deleteOutline(item.id);
            if (result != 'err') {
                readAllValue();
                outlineDataArr.splice(lessonNo, 1);
                renderAndBindAdjustModal();
            }
        })

        $(`.adjustment-${lessonNo} select`).change(function() {
            if ($(this).val() == 5 || $(this).val() == 6) {
                if ($(this).val() == 5) {
                    if (hasReadQuestion) {
                        alert('只能有一道阅读题或其他题型');
                        $(this).find("option[value=5]").removeAttr("selected");
                        $($(this).siblings("input")).val('');
                        return;
                    } 
                } else if ($(this).val() == 6) {
                    if (hasOtherQuestion) {
                        alert('只能有一道阅读题或其他题型');
                        $(this).find("option[value=6]").removeAttr("selected");
                        $($(this).siblings("input")).val('');
                        return;
                    }
                }
                $($(this).siblings("input"))
                .val('1')
                .attr("readonly", true)
            } else {
                $($(this).siblings("input"))
                    .val('')
                    .removeAttr("readonly")
            }
        })

        $(`.adjustment-${lessonNo} input`).change(function() {
            let num = $(this).val();
            if (!(!isNaN(num) && num % 1 === 0 && num > 0)) {
                alert("请输入大于0的整数数字");
                $(this).val("");
                $(this).focus();
            }
            if (num > 20) {
                alert("您的题目过多");
                $(this).val("");
                $(this).focus();
            }
        })

    })

    $(`#adjust-outline`).click(async function() {
        if (isRequesting) return;
        isRequesting = true;
        let obj = {
            'outline_group_ids': [],
            'types': [],
            'qualitys': [],
            'lesson_id': queryObj.lessonId,
            'outline_id': outlineDataArr[0].outline
        };
        outlineDataArr.forEach((item, index) => {
            if (item.id) {
                obj.outline_group_ids.push(item.id);
                obj.types.push(item.type);
                obj.qualitys.push(item.homework_question.length);
            } else {
                obj.outline_group_ids.push('add');
                obj.types.push($(`.adjustment-${index} .select-${index} option:selected`).val());
                obj.qualitys.push($(`.adjustment-${index} .input-${index}`).val() || 1);
            }
        })
        let result = await adjustOutline(obj);
        if (result.code == 0) {
            $('#adjustment').modal('hide');
            window.location.reload();
        } else {
            alert("操作失败");
            outlineDataArr = outlineDataArr.filter(outline => outline.id != null);
            renderAndBindAdjustModal();
        }
        isRequesting = false
    })
}

function renderPreviewModal() {
    outlineDataArr.forEach((item, index) => {
        $('.preview-page-container').append(`
            <div class="subject-${index}">
                <div class="preview-title">
                    <span class="sp-1">${item.name?item.name:typeToheaderlineAndDescription[item.type].headerline}</span>
                    <span class="sp-2"> | </span>
                    <span class="sp-3">${item.remark?item.remark:typeToheaderlineAndDescription[item.type].description}</span>
                </div>
                <div class="question"></div>
            </div>`); 
        // 1. 选择题
        if (item.type == 1) {
            item.homework_question.forEach((j, jIndex) => {
                $(`.question`).eq(index).append(`
                    <div class="chioce-${index}-${jIndex}">
                        <div class="sub-title">${jIndex + 1}. ${j.content.question}<img src="${j.content.questionImage}" class="${j.content.questionImage?'':'hidden'} w100"></div>
                        <div class="preview-single-chioce-options"></div>
                    </div>`);
                // 选项
                j.content.options.forEach((k, kIndex) => {
                    $(`.subject-${index} .chioce-${index}-${jIndex} .preview-single-chioce-options`).append(`
                        <div class="preview-single-chioce-option">
                            <span class="option pl20">${abcdef[kIndex]}${k.answer}</span>
                            <img src="${k.answerImage}" class="${k.answerImage?'':'hidden'} w100">
                        </div>
                    `);
                });
            });
        }
        // 2. 填空题
        if (item.type == 2) {
            item.homework_question.forEach((j, jIndex) => {

                for (let optionIndex = 0; optionIndex < j.content.options.length/3; optionIndex++) {
                    if (optionIndex == 0) {
                        $(`.subject-${index} .question`).append(`    
                            <div class="preview-fill preview-fill-${index}-${jIndex}">
                                <div class="single-fill">
                                    <span class="start">${jIndex + 1}. ${j.content.options[optionIndex*3].sentence}</span>
                                    <div class="ibautowidth">${j.content.options[optionIndex*3+1].sentence}</div>
                                    <span class="end">${j.content.options[optionIndex*3+2].sentence}</span>
                                </div>
                            </div>`
                        );
                    } else {
                        $(`.subject-${index} .question .preview-fill-${index}-${jIndex} .single-fill`).append(`    
                            <span class="start">${j.content.options[optionIndex*3].sentence}</span>
                            <div class="ibautowidth">${j.content.options[optionIndex*3+1].sentence}</div>
                            <span class="end">${j.content.options[optionIndex*3+2].sentence}</span>`
                        );
                    }
                }
            });
        }
        // 3. 连线题
        if (item.type == 3) {
            item.homework_question.forEach((j, jIndex) => {
                $('.question').eq(index).append(`
                <div class="connection-${index}-${jIndex}">
                    <div class="sub-title">${jIndex + 1}.</div>
                    <div class="group-A"></div>
                    <div class="group-B"></div>
                </div>`);

                let groupA = [];
                let groupB = [];
                j.content.options.forEach(q => {
                    $(`.connection-${index}-${jIndex} .group-A`).append(`
                    <div class="m-item">${q.head}<img src="${q.headImage}" class="${q.headImage?'':'hidden'} w100 mr30"></div>
                    `)
                    $(`.connection-${index}-${jIndex} .group-B`).append(`
                    <div class="m-item">${q.tail}<img src="${q.tailImage}" class="${q.tailImage?'':'hidden'} w100 mr30"></div>
                    `)
                });
            });
        }
        // 4. 排序题
        if (item.type == 4) {
            item.homework_question.forEach((j, jIndex) => {
                $('.question').eq(index).append(`    
                    <div class="preview-sort-${index}-${jIndex}">
                        <div class="single-sort">
                            <div class="single-sort-fill">
                            <span class="start">${jIndex + 1}. ${j.content.pre}</span>
                            <span class="input">
                                <input type="" name="" disabled="">
                            </span>
                            <span class="end">${j.content.post}</span>
                            </div>
                            <div class="single-sort-options"></div>
                        </div>
                    </div>`);
                j.content.options.forEach((k, kIndex) => {
                    if (k.word) {
                        $(`.preview-sort-${index}-${jIndex} .single-sort-options`).append(`
                            <div class="option">${k.word}</div>
                        `);
                    }
                });
            });
        }
        // 5. 阅读题
        if (item.type == 5) {
            item.homework_question.forEach((smallSubject, smallIndex) => {
                $(`.subject-${index} .question`).append(`<div class="subject-${index}-${smallIndex}">${smallIndex+1}. 短文</div>`);
                $(`.subject-${index}-${smallIndex}`).append(`<div class="text-align-center">${smallSubject.content}</div>`);

                if (smallSubject.children) {
                    smallSubject.children.forEach((j, jIndex) => {
                        if (j.type == 1) {
                            $(`.subject-${index} .question .subject-${index}-${smallIndex}`).append(`
                                <div class="chioce-${jIndex}">
                                    <div>${jIndex + 1}.${j.name} | ${j.remark} </div>
                                </div>`);
                            j.homework_question.forEach((item, itemIndex) => {
                                $(`.subject-${index} .question .subject-${index}-${smallIndex} > div.chioce-${jIndex}`).append(`
                                    <div class="sub-title">${sortObj[itemIndex]} ${item.content.question}<img src="${item.content.questionImage}" class="${j.homework_question[0].content.questionImage?'':'hidden'} w100"></div>
                                    <div class="preview-single-chioce-options-${itemIndex}"></div>
                                `);
                                // 选项
                                item.content.options.forEach((k, kIndex) => {
                                    $(`.subject-${index} .question .subject-${index}-${smallIndex} .chioce-${jIndex} .preview-single-chioce-options-${itemIndex}`).append(`
                                        <div class="preview-single-chioce-option">
                                            <span class="option">${abcdef[kIndex]} ${k.answer}</span>
                                            <img src="${k.answerImage}" class="${k.answerImage?'':'hidden'} w100">
                                        </div>
                                    `);
                                });
                            })
                        }
                        if (j.type == 2) {
                            $(`.subject-${index} .question .subject-${index}-${smallIndex}`).append(`    
                                <div class="preview-fill mt20">
                                    <div class="mb20">${jIndex + 1}. ${j.name} | ${j.remark}<div>
                                </div>`
                            );
                            j.homework_question.forEach((item, itemIndex) => {
                                for (let optionIndex = 0; optionIndex < j.homework_question[itemIndex].content.options.length/3; optionIndex++) {
                                    if (optionIndex == 0) {
                                        $(`.subject-${index} .question .subject-${index}-${smallIndex} .preview-fill`).append(`   
                                            <div class="single-fill-${itemIndex} mb20">
                                                <span class="start">${sortObj[itemIndex]} ${j.homework_question[itemIndex].content.options[optionIndex*3].sentence}</span>
                                                <div class="ibautowidth">${j.homework_question[itemIndex].content.options[optionIndex*3+1].sentence}</div>
                                                <span class="end">${j.homework_question[itemIndex].content.options[optionIndex*3+2].sentence}</span>
                                            </div> `
                                        );
                                    } else {
                                        $(`.subject-${index} .question .subject-${index}-${smallIndex} .single-fill-${itemIndex}`).append(`
                                            <span class="start">${j.homework_question[itemIndex].content.options[optionIndex*3].sentence}</span>
                                            <div class="ibautowidth">${j.homework_question[itemIndex].content.options[optionIndex*3+1].sentence}</div>
                                            <span class="end">${j.homework_question[itemIndex].content.options[optionIndex*3+2].sentence}</span>
                                        `)
                                    }
                                }
                            })
                        }
                    })
                };
            })
        }
        // 6. 写作题
        if (item.type == 6) {
            if (item.homework_question.length > 0) {
                $('.question').eq(index).append(`    
                <div class="preview-writing">
                    <div class="preview-writing-title-img">
                        <img class="${item.homework_question[0].content.fileType == 2?'':'hidden'}" src="${item.homework_question[0].content.fileUrl}">
                        <iframe class="${item.homework_question[0].content.fileType == 3?'':'hidden'}" src="${item.homework_question[0].content.fileUrl}"></iframe>
                    </div>
                </div>`);
            }
        }
    })
}

function bindUploadEvent() {

    $("#save-homework").click(async function() {
        readAllValue();
        let result = await savaSubjects(0);
        if (result.code == 0) {
            alert('保存成功')
            window.location.reload();
        }
    })

    $("#upload-homework").click(async function() {
        if (isRequesting) return;
        isRequesting = true;
        readAllValue();
        let result = await savaSubjects(1);
        if (result.code == 0) {
            alert("上传成功");
            window.location.reload();
        } else {
            alert("上传失败")
        }
    })

    $("#adjustment-order").click(async function() {
        readAllValue();
        startLoading();
        let result = await savaSubjects(0);
        if (result.code != 0) {
            alert('自动保存失败');
            outlineDataArr = outlineDataArr.filter(outline => outline.id != null);
            endLoading();
            return;
        }
        endLoading();
        $('#adjustment').modal('show');
        $('#adjustment').on('hidden.bs.modal', function (e) {
            renderMakeSubjects()
        })
        renderAndBindAdjustModal();
    })

    $("#homework-preview").click(function() {
        readAllValue();
        $(".preview").modal('show');
        $('.preview').on('hidden.bs.modal', function (e) {
            $('.preview .preview-page-container').children().remove()
        });
        renderPreviewModal()
    })

}

// 保存题目
async function savaSubjects(status) {
    let outline_group = [],
    data = {},
    id;

    if (outlineDataArr.length == 0) return;
    outlineDataArr.forEach(function (item, index) {
        let contentArr = [];
        item.homework_question.forEach(function (contentItem, index) {
            if (item.type == 5) {
                let obj = {};
                obj['id'] = contentItem.id || '';
                obj['htmlArticle'] = contentItem.content;
                obj['knowledge_point_id'] = contentItem['knowledge_point_id']?contentItem['knowledge_point_id']:null;
                obj['knowledge_point_remark'] = contentItem['knowledge_point_remark']?contentItem['knowledge_point_remark']:null;
                obj['children'] = [];
                if (contentItem.children != null) {
                    contentItem.children.forEach((child, index) => {
                        let childObj = {};
                        childObj['outline_group_id'] = child.id || '';
                        childObj['type'] = child.type;
                        childObj['outline_group_name'] = child.name;
                        childObj['outline_group_remark'] = child.remark;
                        childObj['children_question'] = [];
                        // outline_group_name, outline_group_name
                        child.homework_question.forEach((smallSubject, smallIndex) => {
                            let questionObj = {};
                            questionObj['question_id'] = smallSubject.id || '';
                            questionObj = Object.assign(questionObj, smallSubject.content);
                            childObj['children_question'].push(questionObj);
                        })
                        obj['children'].push(childObj)
                    })
                }
                contentArr.push(obj)
            } else {
                contentItem.content['id'] = contentItem.id || '';
                contentArr.push(contentItem.content)
            }
        })
        
        outline_group.push({
            "outline_group_id": item.id,
            "homework": contentArr
        })
    })

    data['outline_id'] = outlineDataArr[0].outline;
    data['lesson_id'] = queryObj.lessonId;
    data['status'] = status;
    data['outline_group'] = outline_group;
    let saveSubject = await jqPromiseAjax({
        url: '/homework/question/add_questions/',
        type: 'POST',
        data: JSON.stringify(data)
    })
    isRequesting = false;
    return saveSubject;
}

async function getKnowledge() {
    let knowledge = await jqPromiseAjax({
        url: ' /homework/knowledge/',
        type: 'get'
    })
    knowledgeList = knowledge;
}


// 不是我写的，不用看
function checkCoursewareSubmit() {
    var mySelect = $('.upload-form select')[0];
    if (mySelect) {
        if (mySelect.selectedIndex >= 0) {
            return true;
        }
    }

    window.alert("请选择课程");
    return false;
}

$(function() {
    if (window.location.pathname == "/man/questions/") {
        var queryArr = location.search.split("&");
        queryObj.lessonId = queryArr[0].split("=")[1];
        queryObj.type = queryArr[1].split("=")[1];

        // 新建大纲重新编辑题目
        getOutline(queryObj.lessonId, 0);

        // 获取知识点
        getKnowledge();

        bindUploadEvent();
        // 0：新增，1：修改
        if (queryObj.type == 1) {
            
        } 
    } else {
        bindingEvent();
    }
})
