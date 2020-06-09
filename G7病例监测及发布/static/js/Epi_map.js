//以下是中国疫情地图部分
var ec_center = echarts.init(document.getElementById("Epi_map"));
//dummy data
var dummy_data = [{ 'name': '上海', 'value': '1' }, { 'name': '重庆', 'value': '23' }, { 'name': '北京', 'value': '323' },
{ 'name': '海南', 'value': '1123' }, { 'name': '西藏', 'value': '523' }, { 'name': '台湾', 'value': '42113' }];
var dummy_data2 = [{ 'name': '上海', 'value': '1' }, { 'name': '重庆', 'value': '23' }, { 'name': '北京', 'value': '3' },
{ 'name': '海南', 'value': '13' }, { 'name': '西藏', 'value': '3' }, { 'name': '台湾', 'value': '42' }];

var choice = dummy_data;
var ec_center_option = {
    title: {
        text: '',
        subtext: '',
        x: 'left'
    },
    tooltip: {
        trigger: 'item'
    },
    //左侧小导航图标
    visualMap: {
        show: true,
        x: 'left',
        y: 'bottom',
        textStyle: {
            fontSize: 8,
        },
        splitList: [{
            start: 1,
            end: 9
        },
        {
            start: 10,
            end: 99
        },
        {
            start: 100,
            end: 999
        },
        {
            start: 1000,
            end: 9999
        },
        {
            start: 10000
        },
        ],
        color: ['#8A3310', '#C64918', '#E55B25', '#F2AD92', '#F9DCD1']
    },
    //配置属性
    series: [{
        name: '累计确诊人数',
        type: 'map',
        mapType: 'china',
        roam: false, //拖动和缩放
        itemStyle: {
            normal: {
                borderWidth: .5, //区域边框宽度
                borderColor: '#009fe8', //区域边框颜色
                areaColor: "#ffefd5", //区域颜色
            },
            emphasis: { //鼠标滑过地图高亮的相关设置
                borderWidth: .5,
                borderColor: '#4b0082',
                areaColor: "#fff",
            }
        },
        label: {
            normal: {
                show: true, //省份名称
                fontSize: 8,
            },
            emphasis: {
                show: true,
                fontSize: 8,
            }
        },
        data: choice //数据
    }]
};
ec_center.setOption(ec_center_option);
//实现点击按钮切换地图类型
$("#changeMap").click(function () {
    if (choice == dummy_data) {
        choice = dummy_data2;
        $("#changeMap").html('切换累积确诊地图');
    }
    else {
        choice = dummy_data;
        $("#changeMap").html('切换现存确诊地图')
    }
	// 重新设置地区
	targetProvince = "全国";
	calcTargetData();
    ec_center.setOption({
        series: [{
            data: choice
        }]
    })
})


//实现点击疫情地图上的省市板块就将对应数据加到趋势图中：
ec_center.on('click', function (param) {
    var region = param['name'];
    var found = 0;
	// 点击的省份与目前展示省份数据相同时，展示全国数据
	if (region == targetProvince)
	{
		targetProvince = "全国";
		for (updatedProvince of choice)
		{
			delete updatedProvince.itemStyle;
		}
	}
	else
	{
		targetProvince = region;
		for (updatedProvince of choice)
		{
			if (updatedProvince.name != region)
			{
				delete updatedProvince.itemStyle;
			}
			else
			{
				updatedProvince.itemStyle = {
					normal: {
						borderColor: "#f70",
						borderWidth: 3,
					}
				}
			}
		}
	}
	
    ec_center.setOption({
        series: [{
            data: choice
        }]
    })
	// 重新加载各趋势图和数据
	calcTargetData();
    for (var index=0;index<optionContrast.series.length;index++) {
        //点击了已经在图上的省市，将之从折线图里面删去。需要删除legend以及series里对应地区的部分
        if (region == optionContrast.series[index].name) {
            found = 1;
            for (index_next = index; index_next < optionContrast.series.length - 1; index_next++) {
                optionContrast.series[index_next] = optionContrast.series[index_next + 1];
            }
            optionContrast.series.pop();
            for (index_next = index; index_next < optionContrast.legend.data.length - 1; index_next++) {
                optionContrast.legend.data[index_next] = optionContrast.legend.data[index_next + 1];
            }
            optionContrast.legend.data.pop();
            contrast.clear();
            break;
        }
    }
    //点击了不在折线图上的省市,将数据加入折线图
    if (!found) {
        var tempList = [];
        for (const index in provinceGather) {
            if (provinceGather[index].proName == region) {
                // contrastLegend.push(region);
                optionContrast.legend.data.push(region);
                for (index_date in provinceGather[index].dayListing) {
                    tempList.push(provinceGather[index].dayListing[index_date].import);
                }
                optionContrast.series.push({name:region,type:'line',data:tempList});

            }
        }

    }

        contrast=echarts.init(document.getElementById('contrastGraph'));
        contrast.setOption(optionContrast);

    //格式
    // provinceGather=[{
    // proName：xxx，dayListing:[{date:'xx', imported:xxx},{},{},{}]
    //},{},{},{}……]]

})


    //格式
    // provinceGather=[{
    // proName：xxx，dayListing:[{date:'xx', imported:xxx},{},{},{}]
    //},{},{},{}……]]


