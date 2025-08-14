# sample code for Streamlit-antd-components
## Icon
import streamlit_antd_components as sac
sac.buttons([sac.ButtonsItem(icon=sac.BsIcon(name='house', size=50))], align='center', variant='text', index=None)

## Buttons
import streamlit_antd_components as sac

sac.buttons([
    sac.ButtonsItem(label='button'),
    sac.ButtonsItem(icon='apple'),
    sac.ButtonsItem(label='google', icon='google', color='#25C3B0'),
    sac.ButtonsItem(label='wechat', icon='wechat'),
    sac.ButtonsItem(label='disabled', disabled=True),
    sac.ButtonsItem(label='link', icon='share-fill', href='https://ant.design/components/button'),
], label='label', align='center')

## Divider
import streamlit_antd_components as sac

sac.divider(label='label', icon='house', align='center', color='gray')

## Menu
import streamlit_antd_components as sac

sac.menu([
    sac.MenuItem('home', icon='house-fill', tag=[sac.Tag('Tag1', color='green'), sac.Tag('Tag2', 'red')]),
    sac.MenuItem('products', icon='box-fill', children=[
        sac.MenuItem('apple', icon='apple'),
        sac.MenuItem('other', icon='git', description='other items', children=[
            sac.MenuItem('google', icon='google', description='item description'),
            sac.MenuItem('gitlab', icon='gitlab'),
            sac.MenuItem('wechat', icon='wechat'),
        ]),
    ]),
    sac.MenuItem('disabled', disabled=True),
    sac.MenuItem(type='divider'),
    sac.MenuItem('link', type='group', children=[
        sac.MenuItem('antd-menu', icon='heart-fill', href='https://ant.design/components/menu#menu'),
        sac.MenuItem('bootstrap-icon', icon='bootstrap-fill', href='https://icons.getbootstrap.com/'),
    ]),
], open_all=True)

## Steps
import streamlit_antd_components as sac

sac.steps(
    items=[
        sac.StepsItem(title='step 1', subtitle='extra msg', description='description text'),
        sac.StepsItem(title='step 2'),
        sac.StepsItem(title='step 3'),
        sac.StepsItem(title='step 4', disabled=True),
    ], format_func='title', size='lg', color='orange', placement='vertical'
)

## Checkbox
import streamlit_antd_components as sac

sac.checkbox(
    items=[
        'item1',
        'item2',
        'item3',
        sac.CheckboxItem('item4', disabled=True)
    ],
    label='label', index=[0, 1], align='center'
)

## Chip
import streamlit_antd_components as sac

sac.chip(
    items=[
        sac.ChipItem(label='apple'),
        sac.ChipItem(icon='google'),
        sac.ChipItem(label='github', icon='github'),
        sac.ChipItem(label='twitter', icon='twitter'),
        sac.ChipItem(label='disabled', disabled=True),
    ], label='label', index=[0, 2], align='center', radius='md', multiple=True
)

## Switch
import streamlit_antd_components as sac

sac.switch(label='label', align='center', size='md')

## Tabs
import streamlit_antd_components as sac

sac.tabs([
    sac.TabsItem(label='apple', tag="10"),
    sac.TabsItem(icon='google'),
    sac.TabsItem(label='github', icon='github'),
    sac.TabsItem(label='disabled', disabled=True),
], format_func='title', height=150, size='lg')

## Tree
import streamlit_antd_components as sac

sac.tree(items=[
    sac.TreeItem('item1', tag=[sac.Tag('Tag', color='red'), sac.Tag('Tag2', color='cyan')]),
    sac.TreeItem('item2', icon='apple', description='item description', children=[
        sac.TreeItem('tooltip', icon='github', tooltip='item tooltip'),
        sac.TreeItem('item2-2', children=[
            sac.TreeItem('item2-2-1'),
            sac.TreeItem('item2-2-2'),
            sac.TreeItem('item2-2-3'),
        ]),
    ]),
    sac.TreeItem('disabled', disabled=True),
    sac.TreeItem('item3', children=[
        sac.TreeItem('item3-1'),
        sac.TreeItem('item3-2'),
    ]),
], label='label', index=0, format_func='title', align='center', size='md', open_all=True, return_index=True)

