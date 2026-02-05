from django.db import migrations


VIEW_SQL = """
CREATE OR REPLACE VIEW AllUserInfo_View AS

SELECT
    
    ui.user_id,
    ui.user_name,
    ui.user_email,
    ui.user_password,
    ui.user_date_of_creation,
    ui.user_lat_passcode_update,
    ui.user_active,
    ui.user_deleted,
    ui.user_role,
    ui.user_photo_path,
    ui.user_photo_link,
    ui.user_fullname,

    
    li.login_session_id,
    li.login_date_time,
    li.jwt_token,
    li.is_active AS login_is_active,
    li.created_at,
    li.expires_at,

    
    ti.team_id,
    ti.team_name,
    ti.team_created_by,
    ti.team_created_datetime,
    ti.team_deleted,

    
    tu.team_uer_team_role,
    tu.team_user_date_of_creation,
    tu.team_user_active,
    tu.team_user_deleted

FROM app1_userinfo ui

LEFT JOIN app1_userlogininfo li
    ON li.user_id = ui.user_id

LEFT JOIN app1_teamusers tu
    ON tu.user_id = ui.user_id

LEFT JOIN app1_teaminfo ti
    ON ti.team_id = tu.team_id;
"""


DROP_SQL = """
DROP VIEW IF EXISTS AllUserInfo_View;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=VIEW_SQL,
            reverse_sql=DROP_SQL,
        ),
    ]