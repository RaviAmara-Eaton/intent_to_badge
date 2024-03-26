import streamlit as st
import pandas as pd

# Session Initializations
cnx=st.connection("snowflake")
session = cnx.session()
if 'auth_status' not in st.session_state:
    st.session_state['auth_status'] = 'not_authed'
if 'display_format' not in st.session_state:
    st.session_state['display_format'] = 1

# Temp for debugging
st.session_state

# Page Header
st.header('Are You Snow-A-Mazing?')
st.write('Welcome to the learn.snowflake.com Workshop Badge Management app!')

uni_id = st.text_input('Enter your learn.snowflake.com UNI ID:')
uni_uuid = st.text_input('Enter the secret UUID displayed on the DORA is Listening Page:')
find_my_uni_record = st.button("Find my UNI User Info")

if find_my_uni_record:
    # reset all session vars
    st.session_state['auth_status'] = 'not_authed'
    st.session_state['uni_id'] = uni_id
    st.session_state['uni_uuid'] = uni_uuid
    st.session_state['given_name'] = ''
    st.session_state['middle_name'] = ''
    st.session_state['family_name'] = ''
    st.session_state['badge_email'] = ''
    
    this_user_sql =  "select badge_given_name, badge_middle_name, badge_family_name, badge_email, display_format, coalesce(display_name,'<no display name generated>') as display_name from UNI_USER_BADGENAME_BADGEEMAIL where UNI_ID=trim('" + uni_id + "') and UNI_UUID=trim('"+ uni_uuid +"')"
    this_user_df = session.sql(this_user_sql)
    user_results = this_user_df.to_pandas()                          
    user_rows = user_results.shape[0]
    st.dataframe(user_results)
    
    if user_rows>=1:
        st.session_state['auth_status'] = 'authed'
        st.session_state['uni_id'] = uni_id
        st.session_state['given_name'] = user_results['BADGE_GIVEN_NAME'].iloc[0]
        st.session_state['middle_name'] = user_results['BADGE_MIDDLE_NAME'].iloc[0]
        st.session_state['family_name'] = user_results['BADGE_FAMILY_NAME'].iloc[0]
        st.session_state['badge_email'] = user_results['BADGE_EMAIL'].iloc[0]
        st.session_state['display_format'] = user_results['DISPLAY_FORMAT'].iloc[0]    
        st.session_state['display_name'] = user_results['DISPLAY_NAME'].iloc[0]
    else:
        st.markdown(":red[There is no record of the UNI_ID/UUID combination you entered. Please double-check the info you entered, read the tips on the FINDING INFO tab, and try again]") 

###################################### Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["View Name/Email", "Edit Name/Email","Choose Name Display", "My Badge Work", "FAQs"])

with tab1:
    st.subheader("Your Name and Email - Currently Stored in Our System")
    if st.session_state.auth_status == 'authed':
        st.markdown("**GIVEN NAME:** " + st.session_state.given_name)
        st.markdown("**MIDDLE/ALTERNATE NAME:** "+ st.session_state.middle_name) 
        st.markdown("**FAMILY NAME:** " + st.session_state.family_name)
        st.markdown("**EMAIL:** " + st.session_state.badge_email)
        st.markdown("**Name Will Display on Badge As:** " + st.session_state.display_name)
        st.write("-----")
        st.markdown("*If your display name has not been generated, or you would like to make changes to information, go to the next tab and edit your information*")
    else:
        st.write("Please sign in using your UNI_ID and UUID in the section above.")
###################################
with tab2:
    st.subheader("Edit or Confirm Your Name for Your Badge(s)")

    if st.session_state.auth_status == 'authed':
        with st.form("badge_name_and_email"):
            st.write("Confirm Your Name for Any Badges That Might Be Issued")     
            edited_given = st.text_input("Given Name (Name used to greet you)", st.session_state.given_name)
            edited_middle = st.text_input('Middle Name/Nickname/Alternate-Spelling (Optional)', st.session_state.middle_name)
            edited_family = st.text_input('Family Name', st.session_state.family_name)
            edited_email = st.text_input("The Email Address You Want Your Badge Sent To (does not have to match UNI, Snowflake Trial, or Work):", st.session_state.badge_email)
            submit_edits = st.form_submit_button("Update My Badge Name & Badge Email")  

        if submit_edits:
            session.call('AMAZING.APP.UPDATE_BADGENAME_BADGEEMAIL_SP',uni_id, uni_uuid, edited_given, edited_middle, edited_family, edited_email)
            st.success('Badge Name & Email Updated', icon='🚀')

    else: # not authed
        st.write("Please sign in using your UNI_ID and UUID in the section above.")  
#######################################
with tab3:
    st.subheader("Format the Display of Your Name on Your Badge(s)")

    if st.session_state.auth_status == 'authed':
        with st.form("display_formatting"):
            display_option_1 = edited_given.capitalize() + " " + edited_middle.capitalize() + " " + edited_family.capitalize() #lazy do it for me
            display_option_2 = edited_given.capitalize() + " " + edited_middle.capitalize() + " " + edited_family #european w nobiliary
            display_option_3 = edited_family.upper() + " " + edited_middle + " " + edited_given.capitalize()  #east asian with alt script middle
            display_option_4 = edited_family.upper() + " " +  edited_given.capitalize() + " " + edited_middle.capitalize() #east asian with alt script middle
            display_option_5 = edited_given.capitalize() + " " +  edited_middle.capitalize() + " " + edited_family.upper() #ze french
                
            badge_name_order = st.radio("Name Display Order You Prefer:",                            
                                  [display_option_1, display_option_2, display_option_3, display_option_4, display_option_5],
                                  captions = ["Common in Anglo Traditions", "For names with nobiliary particles", "For use with dual script like 전 JEON Joon-kook 정국 ", "For cultures that put FAMILY name first", "Common for French and Francophonic"]
                                   )
            submit_display_format = st.form_submit_button("Record My Name Display Preference")
        
        if submit_display_format:
            if badge_name_order == display_option_1:
                display_format = 1
                edited_display_name = display_option_1
                    
            elif badge_name_order == display_option_2:
                display_format = 2
                edited_display_name = display_option_2
                    
            elif badge_name_order == display_option_3:
                display_format = 3
                edited_display_name = display_option_3
                    
            elif badge_name_order == display_option_4:
                display_format = 4
                edited_display_name = display_option_4
                    
            elif badge_name_order == display_option_5:
                display_format = 5
                edited_display_name = display_option_5
            else: 
                st.write('Choose a format for your name')
                    
            session.call('AMAZING.APP.UPDATE_BADGE_DISPLAYNAME_SP',uni_id, uni_uuid, display_format, edited_display_name)
            st.success('Badge Display Name Updated', icon='🚀')

##########################################
with tab4:
    st.subheader("View Trial Account and Badges Awarded Information")
    
    if st.session_state.auth_status == 'authed':
        badge_options = pd.DataFrame({'badge_name':['Badge 1: DWW', 'Badge 2: CMCW', 'Badge 3: DABW', 'Badge 4: DLKW', 'Badge 5: DNGW'], 'award_name':['AWARD-DWW','AWARD-CMCW','AWARD-DABW','AWARD-DLKW','AWARD-DNGW']})
        # st.dataframe(badge_options)
        workshop = st.selectbox("Choose Workshop/Badge want to enter/edit account info for:", options=badge_options, key=1)
        st.session_state['workshop_acro'] = workshop[9:13]
        award_name = 'AWARD-'+st.session_state.workshop_acro
        
        workshop_sql =  "select award_id, account_locator, organization_id, account_name from AMAZING.APP.USER_ACCOUNT_INFO_BY_COURSE where type = 'MAIN' and UNI_ID=trim('" + uni_id + "') and UNI_UUID=trim('"+ uni_uuid +"') and AWARD_ID = '" + award_name + "'"
        workshop_df = session.sql(workshop_sql)
        workshop_results = workshop_df.to_pandas()
        workshop_rows = workshop_results.shape[0]
        
        if workshop_rows>=1:
            st.write("We found your Trial Account Info. Please make sure it is complete!")
            if (workshop_results.iloc[0]['ACCOUNT_LOCATOR'] is not None):
                st.write("Your Account LOCATOR for " + workshop + " is: " + workshop_results.iloc[0]['ACCOUNT_LOCATOR'])
            if (workshop_results.iloc[0]['ORGANIZATION_ID'] is not None):    
                st.write("Your Account ORGANIZATION for " + workshop + " is: " +workshop_results.iloc[0]['ORGANIZATION_ID'] or "Missing")
            if (workshop_results.iloc[0]['ACCOUNT_NAME'] is not None):
                st.write("Your ACCOUNT NAME for " + workshop + " is: " + workshop_results.iloc[0]['ACCOUNT_NAME'] or "Missing")
        else:
            st.write("If you intend to pursue the " + st.session_state.workshop_acro + " badge, you should click the Register button below.")
            new_badge_interest = st.button("Register for the " + st.session_state.workshop_acro + " Badge")

            if new_badge_interest:
                with st.form("new_workshop_interest"):
                    new_acct_id = st.text_input("Enter the ACCOUNT ID of Your Snowflake Trial Account:")
                    new_acct_loc = st.text_input("Enter the ACCOUNT LOCATOR of Your Snowflake Trial Account:")
                    new_info_submit = st.form_submit_button("Submit My New Trial Account Info") 
                    if new_info_submit:
                        add_workshop_result = session.call('AMAZING.APP.ADD_ACCT_INFO_SP',st.session_state.uni_id, st.session_state.uni_uuid, st.session_state.workshop_acro, new_acct_id, new_acct_loc)
                        # st.session_state['add_workshop'] = add_workshop_result
                        # st.error(e, icon="🚨")
                    st.success('Snowflake Trial Account Info Updated for ' + workshop, icon='🚀')
            
       
    
        
        #with st.form("workshops"):  
         #   st.write("editing will happen here")
         #   workshop_chosen = st.form_submit_button("Show Data on My Chosen Workshop")
