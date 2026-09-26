import duckdb
import logging
import sys

logging.getLogger(__name__)

def owner_license(owner_df, license_df):
    logging.info('..Joining datasets')
    join_sql = """
                WITH joined as (     
                    WITH license AS (
                    SELECT 
                        id,
                        license_id,
                        account_number,
                        site_number,
                        legal_name,
                        doing_business_as_name,
                        address,
                        city,
                        state,
                        zip_code,
                        ward,
                        precinct,
                        ward_precinct,
                        police_district,
                        community_area,
                        community_area_name,
                        neighborhood,
                        license_code,
                        license_description,
                        license_number,
                        application_type,
                        application_created_date::date as application_created_date,
                        application_requirements_complete,
                        payment_date,
                        business_activity_id,
                        business_activity,
                        ssa,
                        license_status_change_date,
                        conditional_approval,
                        license_start_date,
                        expiration_date,
                        license_approved_for_issuance,
                        date_issued,
                        license_status,
                        latitude,
                        longitude,
                        --location,
                        sys_id AS sys_id_license,
                        sys_version AS sys_version_license,
                        sys_created_at AS sys_created_at_license,
                        sys_updated_at AS sys_updated_at_license,
                        sys_computed_region_vrxf_vc4k AS sys_computed_region_vrxf_vc4k_license,
                        sys_computed_region_awaf_s7ux AS sys_computed_region_awaf_s7ux_license,
                        sys_computed_region_6mkv_f3dw AS sys_computed_region_6mkv_f3dw_license,
                        sys_computed_region_bdys_3d7i AS sys_computed_region_bdys_3d7i_license,
                        sys_computed_region_43wa_7qmu AS sys_computed_region_43wa_7qmu_license
                    FROM license_df
                    )
                    SELECT 
                        COALESCE(od.account_number::text,'') AS account_number,
                        COALESCE(od.doing_business_as_name,'') AS doing_business_as_name,
                        COALESCE(od.owner_last_name,'NLN') || ',' || COALESCE(od.owner_first_name,'NFN') || ' ' || COALESCE(od.owner_middle_initial,'NMI') AS full_name,
                        COALESCE(od.owner_first_name,'') AS owner_first_name,
                        COALESCE(od.owner_last_name,'') AS owner_last_name,
                        COALESCE(od.owner_title,'') AS owner_title,
                        COALESCE(od.owner_middle_initial,'') AS owner_middle_initial,
                        COALESCE(od.owner_name,'') AS owner_name,
                        COALESCE(od.owner_name_suffix,'') AS owner_name_suffix,
                        COALESCE(ld.id,'') AS id,
                        COALESCE(ld.license_id,'') AS license_id,
                        COALESCE(ld.site_number,'') AS site_number,
                        COALESCE(ld.legal_name,'') AS legal_name,
                        COALESCE(ld.doing_business_as_name,'') AS doing_business_as_name,
                        COALESCE(ld.address,'') AS address,
                        COALESCE(ld.city,'') AS city,
                        COALESCE(ld.state,'') AS state,
                        COALESCE(ld.zip_code,'') AS zip_code,
                        COALESCE(ld.ward::NUMERIC,-1) AS ward,
                        COALESCE(ld.precinct::NUMERIC,-1) AS precinct,
                        COALESCE(ld.ward_precinct,'') AS ward_precinct,
                        COALESCE(ld.police_district::NUMERIC,-1) AS police_district,
                        COALESCE(ld.community_area::NUMERIC,-1) AS community_area,
                        COALESCE(ld.community_area_name,'') AS community_area_name,
                        COALESCE(ld.neighborhood,'') AS neighborhood,
                        COALESCE(ld.license_code::NUMERIC,-1) AS license_code,
                        COALESCE(ld.license_description,'') AS license_description,
                        COALESCE(ld.license_number::NUMERIC,-1) AS license_number,
                        COALESCE(ld.application_type,'') AS application_type,
                        COALESCE(ld.application_created_date::date,NULL) AS application_created_date,
                        COALESCE(ld.application_requirements_complete,NULL) AS application_requirements_complete,
                        COALESCE(ld.payment_date,NULL) AS payment_date,
                        COALESCE(ld.business_activity_id,'') AS business_activity_id,
                        COALESCE(ld.business_activity,'') AS business_activity,
                        COALESCE(ld.ssa,'') AS ssa,
                        COALESCE(ld.license_status_change_date,NULL) AS license_status_change_date,
                        COALESCE(ld.conditional_approval,NULL) AS conditional_approval,
                        COALESCE(ld.license_start_date,NULL) AS license_start_date,
                        COALESCE(ld.expiration_date,NULL) AS expiration_date,
                        COALESCE(ld.license_approved_for_issuance,NULL) AS license_approved_for_issuance,
                        COALESCE(ld.date_issued,NULL) AS date_issued,
                        COALESCE(ld.license_status,'') AS license_status,
                        COALESCE(ld.latitude::NUMERIC,-1) AS latitude,
                        COALESCE(ld.longitude::NUMERIC,-1) AS longitude,
                        --ld.location,  -- Is a nested json that contains data from columns provided above
                        od.sys_id AS sys_id_owner,
                        od.sys_version AS sys_version_owner,
                        od.sys_created_at AS sys_created_at_owner,
                        od.sys_updated_at AS sys_updated_at_owner,
                        ROW_NUMBER() OVER (PARTITION BY COALESCE(od.account_number::text,''),
                                            COALESCE(UPPER(od.doing_business_as_name),''),
                                            COALESCE(UPPER(od.owner_first_name),''),
                                            COALESCE(UPPER(od.owner_last_name),''),
                                            COALESCE(UPPER(od.owner_title),''),
                                            COALESCE(UPPER(od.owner_middle_initial),''),
                                            COALESCE(UPPER(od.owner_name),''),
                                            COALESCE(UPPER(od.owner_name_suffix),'')) AS rn,
                        ld.sys_id_license,
                        ld.sys_version_license,
                        ld.sys_created_at_license,
                        ld.sys_updated_at_license,
                        ld.sys_computed_region_vrxf_vc4k_license,
                        ld.sys_computed_region_awaf_s7ux_license,
                        ld.sys_computed_region_6mkv_f3dw_license,
                        ld.sys_computed_region_bdys_3d7i_license,
                        ld.sys_computed_region_43wa_7qmu_license
                    FROM owner_df od
                    LEFT JOIN license ld ON (od.account_number = ld.account_number)
                )
                SELECT *
                FROM joined
                WHERE rn = 1;
                """
    try: 
        logging.info(f'..Executing\n {join_sql}')
        joined_data = duckdb.sql(join_sql).df()
        logging.info(f'..Success : {joined_data.shape}')
        return joined_data
    except (duckdb.BinderException, duckdb.ParserException) as e:
        logging.error(e)
        sys.exit(1)
        