
// 初始化各echarts实例
var trendChart1 = echarts.init(document.getElementById('trendNationWide'));
var trendChart2 = echarts.init(document.getElementById('trendTotal'));
var trendChart3 = echarts.init(document.getElementById('trendDaily'));

// 样例数据，等待同步后端的数据。
// 注意：请确保传回数据中各省份日期序列相同且按时间顺序排列！！
var data = [{
    province: "浙江",
    data: [{
        date: "03-01", diagnosed: 100, imported: 10,
        asymptomatic: 15, cured: 5, dead: 1
    },
    {
        date: "03-02", diagnosed: 90, imported: 9,
        asymptomatic: 20, cured: 10, dead: 2
    },
    {
        date: "03-03", diagnosed: 80, imported: 2,
        asymptomatic: 17, cured: 15, dead: 0
    }]
},
{
    province: "江苏",
    data: [{
        date: "03-01", diagnosed: 70, imported: 5,
        asymptomatic: 12, cured: 13, dead: 1
    },
    {
        date: "03-02", diagnosed: 30, imported: 6,
        asymptomatic: 32, cured: 43, dead: 0
    },
    {
        date: "03-03", diagnosed: 40, imported: 7,
        asymptomatic: 14, cured: 24, dead: 1
    }]
},
{
    province: "湖北",
    data: [{
        date: "03-01", diagnosed: 70, imported: 6,
        asymptomatic: 12, cured: 13, dead: 1
    },
    {
        date: "03-02", diagnosed: 30, imported: 30,
        asymptomatic: 32, cured: 43, dead: 0
    },
    {
        date: "03-03", diagnosed: 40, imported: 1,
        asymptomatic: 14, cured: 24, dead: 1
    }]
}
];
// 样例目标省份。可填各省名称、"全国"、"非湖北"
var targetProvince = "浙江";


// 计算全国及目标地区各日数据
var nationwideData = []; // 绘制用数据
for (const provinceN in data) {
    province = data[provinceN];
    for (const dataN in province.data) {
        // 计算全国累计治愈、死亡
        dateData = province.data[dataN];
        if (provinceN == 0) {
            nationwideData.push({
                date: dateData.date,
                diagnosed: dateData.diagnosed,
                cured: dateData.cured,
                dead: dateData.dead
            });
        } else {
            toModifiedData = nationwideData[dataN];
            toModifiedData.diagnosed += dateData.diagnosed;
            toModifiedData.cured += dateData.cured;
            toModifiedData.dead += dateData.dead;
        }
    }
}

// 计算全国治愈率、死亡率趋势
var nationwideRateData = [];
var totalDiagnosed = 0, totalDead = 0, totalCured = 0;
for (const dateData of nationwideData) {
    totalDiagnosed += dateData.diagnosed;
    totalCured += dateData.cured;
    totalDead += dateData.dead;
    nationwideRateData.push({
        date: dateData.date,
        curedRate: (totalCured / totalDiagnosed * 100).toFixed(1),
        deadRate: (totalDead / totalDiagnosed * 100).toFixed(1)
    });
}

// 变量与文字对应关系
var seriesText1 = {
    curedRate: "治愈率",
    deadRate: "死亡率"
};
var seriesText2 = {
    totalDiagnosed: "累计确诊",
    totalDead: "累计死亡",
    totalCured: "累计治愈"
};
var seriesText3 = {
    diagnosed: "新增确诊"
};

// 全国治愈率、死亡率趋势图数据配置
var optionTC1 = {
    title: {
        text: '全国治愈率、死亡率趋势图'
    },
    tooltip: {
        formatter: function (params) {
            tipString = "日期：" + params.data.date + "<br>";
            tipString = tipString + seriesText1[params.seriesName] + "：";
            tipString = tipString + params.data[params.seriesName] + "%";
            return tipString;
        },
        textStyle: {
            align: 'left'
        }
    },
    legend: {
        x: "left",
        y: "bottom",
        formatter: function (params) {
            return seriesText1[params];
        }
    },
    xAxis: { type: 'category' },
    yAxis: {},
    series: [
        { type: "line" },
        { type: "line" }
    ],
    dataset: {
        dimensions: ['date', 'curedRate', 'deadRate'],
        source: nationwideRateData
    }
};

// 使用刚指定的配置项和数据显示图表。
trendChart1.setOption(optionTC1);

// 计算各省累计、新增数据并显示图表。之所以单独作为函数是因为这一块可能会被反复调用，因此以重复遍历为代价增强复用性。
function calcTargetData() {
    // 计算目标地区新增数据
    var targetData = []; // 绘制用数据
    var firstProvince = 1; // 判断是否为第一个录入的省份
    for (const province of data) {
        if (province.province == targetProvince || targetProvince == "全国" || (targetProvince == "非湖北" && province.province != "湖北")) {
            for (const dataN in province.data) {
                dateData = province.data[dataN];
                if (firstProvince == 1) {
                    targetData.push({
                        date: dateData.date,
                        diagnosed: dateData.diagnosed,
                        cured: dateData.cured,
                        dead: dateData.dead
                    });
                } else {
                    toModifiedData = targetData[dataN];
                    toModifiedData.diagnosed += dateData.diagnosed;
                    toModifiedData.cured += dateData.cured;
                    toModifiedData.dead += dateData.dead;
                }
            }
        	firstProvince = 0;
        }
    }
    // 计算目标地区累计确诊、死亡、治愈
    var totalDiagnosed = 0, totalCured = 0, totalDead = 0;
    for (dateData of targetData) {
        totalDiagnosed += dateData.diagnosed;
        totalCured += dateData.cured;
        totalDead += dateData.dead;
        dateData.totalDiagnosed = totalDiagnosed;
        dateData.totalCured = totalCured;
        dateData.totalDead = totalDead;
    }

    // 显示目标地区累计确诊、死亡、治愈趋势图
    var optionTC2 = {
        title: {
            text: '各地累计确诊、死亡、治愈趋势图'
        },
        tooltip: {
            formatter: function (params) {
                tipString = "日期：" + params.data.date + "<br>";
                tipString = tipString + seriesText2[params.seriesName] + "：";
                tipString = tipString + params.data[params.seriesName];
                return tipString;
            },
            textStyle: {
                align: 'left'
            }
        },
        legend: {
            x: "left",
            y: "bottom",
            formatter: function (params) {
                return seriesText2[params];
            }
        },
        xAxis: { type: 'category' },
        yAxis: {},
        series: [
            { type: "line" },
            { type: "line" },
            { type: "line" }
        ],
        dataset: {
            dimensions: ['date', 'totalDiagnosed', 'totalDead', 'totalCured'],
            source: targetData
        }
    };
    trendChart2.setOption(optionTC2);

    // 显示目标地区每日新增确诊趋势图
    var optionTC3 = {
        title: {
            text: '各地每日新增确诊对比图'
        },
        tooltip: {
            formatter: function (params) {
                tipString = "日期：" + params.data.date + "<br>";
                tipString = tipString + seriesText3[params.seriesName] + "：";
                tipString = tipString + params.data[params.seriesName];
                return tipString;
            },
            textStyle: {
                align: 'left'
            }
        },
        legend: {
            x: "left",
            y: "bottom",
            formatter: function (params) {
                return seriesText3[params];
            }
        },
        xAxis: { type: 'category' },
        yAxis: {},
        series: [
            { type: "line" }
        ],
        dataset: {
            dimensions: ['date', 'diagnosed'],
            source: targetData
        }
    };
    trendChart3.setOption(optionTC3);
}
calcTargetData();
//modify
//趋势图部分
var contrast = echarts.init(document.getElementById('contrastGraph'));
var contrastLegend = ['湖北'], contrastXaxis = [];
var contrastSeries = [];
var provinceGather = [];
for (const index in data) {
    var proName = data[index].province;
    //contrastLegend.push(proName);
    var dayListingThisProvince = [];
    for (const everyday in data[index].data) {
        dayListingThisProvince.push(
            {
                date: data[index].data[everyday].date,
                import: data[index].data[everyday].imported
            }
        )
    }
    provinceGather.push(
        {
            proName: proName,
            dayListing: dayListingThisProvince
        }
    )
}

var tempList = [];
for (const index in provinceGather) {
    if (provinceGather[index].proName == '湖北') {
        for (const index_date in provinceGather[index].dayListing) {
            tempList.push(provinceGather[index].dayListing[index_date].import);
            contrastXaxis.push(provinceGather[index].dayListing[index_date].date);
        }
        contrastSeries.push({
            name: '湖北',
            type: 'line',
            data: tempList}
        );
    }
}

optionContrast = {
    title: {
        text: '每日境外输入趋势图'
    },
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        data: contrastLegend,
        x:"left",
        y:"bottom"
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        data: contrastXaxis
    },
    yAxis: {
        type: 'value'
    },
    series: contrastSeries
};
contrast.setOption(optionContrast);


//modify

// 当画面大小变化时对应改变各图表的尺寸。
function resizeCharts() {
    $("#trendNationWide").css({
        "height": 0.6 * $("#trendNationWideDiv").width(),
        "width": $("#trendNationWideDiv").width()
    });
    trendChart1.resize();
    $("#trendTotal").css({
        "height": 0.6 * $("#trendTotalDiv").width(),
        "width": $("#trendTotalDiv").width()
    });
    trendChart2.resize();
    $("#trendDaily").css({
        "height": 0.6 * $("#trendDailyDiv").width(),
        "width": $("#trendDailyDiv").width()
    });
    trendChart3.resize();
    $("#contrastGraph").css({
        "height": 0.6 * $("#contrastWrapper").width(),
        "width": $("#contrastWrapper").width()

    })
    contrast.resize();
}




// 不要忘记设置图表的初始大小。
$(document).ready(function () {
    resizeCharts();
})

// 使图表大小进行自适应。
window.onresize = function () {
    resizeCharts();
}
