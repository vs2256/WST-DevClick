Rem Follow the below steps before running the bat file
Rem replace the list of ownerIds in the for loop with the ownerIds required
cd ${WORKSPACE_BASE_PATH}
if not exist ${MOUNT_FOLDER_NAME} mkdir ${MOUNT_FOLDER_NAME}
cd ${MOUNT_FOLDER_NAME}
if not exist ${RFX_APP_NAME} mkdir ${RFX_APP_NAME}
if not exist ${KERNEL_CONFIG_FOLDER} mkdir ${KERNEL_CONFIG_FOLDER}
cd ${RFX_APP_NAME}
if not exist applogs mkdir applogs
if not exist appuploads mkdir appuploads
if not exist staticconfig mkdir staticconfig
if not exist staticweb mkdir staticweb
cd ${MOUNT_BASE_PATH}\appuploads
if not exist upload mkdir upload
if not exist qatestcases mkdir qatestcases
for %%x in (${RWS4_OWNER_IDS}) do (
cd ${MOUNT_BASE_PATH}\appuploads\qatestcases
if not exist notifications mkdir notifications
cd ${MOUNT_BASE_PATH}\appuploads\qatestcases\notifications 
mkdir %%x
cd ${MOUNT_BASE_PATH}\appuploads\upload
if not exist ${MOUNT_BASE_PATH}\appuploads\upload\%%x (
mklink /J %%x "${REPO_PRIMARY_PATH}\WebContent\upload"
cd ${MOUNT_BASE_PATH}\staticconfig
mkdir %%x
cd ${MOUNT_BASE_PATH}\staticconfig\%%x
mklink /J algorithms "${REPO_PRIMARY_PATH}\WebContent\algorithms"
mklink /J config "${REPO_PRIMARY_PATH}\WebContent\config"
mklink /J reports "${REPO_PRIMARY_PATH}\WebContent\reports"
mklink /J templates "${REPO_PRIMARY_PATH}\WebContent\templates"
mklink /J workflows "${REPO_PRIMARY_PATH}\WebContent\workflows"
mklink /H File_Address.ini "${REPO_PRIMARY_PATH}\WebContent\File_Address.ini"
mkdir WEB-INF
cd ${MOUNT_BASE_PATH}\staticconfig\%%x\WEB-INF
mklink /H ReflexisScheduler.xml "${REPO_PRIMARY_PATH}\WebContent\WEB-INF\ReflexisScheduler.xml"
mkdir classes
cd classes
mkdir com
cd com
mkdir reflexis
cd reflexis
mkdir i18n
cd i18n
mklink /J resourcebundles "${REPO_PRIMARY_PATH}\src\com\reflexis\i18n\resourcebundles"
cd ${MOUNT_BASE_PATH}\staticweb
if not exist images mkdir images
cd ${MOUNT_BASE_PATH}\staticweb\images
mklink /J %%x "${REPO_PRIMARY_PATH}\WebContent\images" 
)
)
cd ${MOUNT_BASE_PATH}\staticweb\images
if not exist ${MOUNT_BASE_PATH}\staticweb\images\DEFAULT mklink /J DEFAULT "${REPO_PRIMARY_PATH}\WebContent\images" 
cd ${MOUNT_BASE_PATH}\staticconfig
if not exist DEFAULT mkdir DEFAULT
cd ${MOUNT_BASE_PATH}\staticconfig\DEFAULT
if not exist ${MOUNT_BASE_PATH}\staticconfig\DEFAULT\H mklink /H log4j.xml "${REPO_PRIMARY_PATH}\WebContent\WEB-INF\log4j.xml"
if not exist ${MOUNT_BASE_PATH}\staticconfig\DEFAULT\J mklink /J property "${REPO_PRIMARY_PATH}\WebContent\WEB-INF\property"
if not exist ${MOUNT_BASE_PATH}\staticconfig\DEFAULT\J mklink /J apiDoc "${REPO_PRIMARY_PATH}\WebContent\templates\apiDoc"
if not exist config mkdir config
cd ${MOUNT_BASE_PATH}\staticconfig\DEFAULT\config
if not exist ${MOUNT_BASE_PATH}\staticconfig\DEFAULT\config\H mklink /H i18nConfig.json "${REPO_PRIMARY_PATH}\WebContent\config\i18nConfig.json"
cd ${MOUNT_BASE_PATH}\staticconfig\DEFAULT
if not exist WEB-INF mkdir WEB-INF
cd ${MOUNT_BASE_PATH}\staticconfig\DEFAULT\WEB-INF
if not exist classes  mkdir classes
cd ${MOUNT_BASE_PATH}\staticconfig\DEFAULT\WEB-INF\classes
if not exist com  mkdir com
cd com
if not exist reflexis  mkdir reflexis
cd reflexis
if not exist i18n  mkdir i18n
cd i18n
if not exist ${MOUNT_BASE_PATH}\staticconfig\DEFAULT\WEB-INF\classes\com\reflexis\i18n\resourcebundles  mklink /J resourcebundles "${REPO_PRIMARY_PATH}\src\com\reflexis\i18n\resourcebundles"
cd ${MOUNT_BASE_PATH}\applogs
if not exist global mkdir global
cd global
if not exist METRIC_QUEUE mkdir METRIC_QUEUE
cd ${MOUNT_BASE_PATH}\applogs\global
type NUL > InboxProcessingBatch.log
type NUL > ReflexisScheduler.log
type NUL > UnitPayStatus.log
cd ${MOUNT_BASE_PATH}\staticweb
if not exist ${MOUNT_BASE_PATH}\staticweb\css mklink /J css "${REPO_PRIMARY_PATH}\WebContent\css"
if not exist ${MOUNT_BASE_PATH}\staticweb\css_rta mklink /J css_rta "${REPO_PRIMARY_PATH}\WebContent\css_rta"
if not exist ${MOUNT_BASE_PATH}\staticweb\dashboard mklink /J dashboard "${REPO_PRIMARY_PATH}\WebContent\dashboard"
if not exist ${MOUNT_BASE_PATH}\staticweb\fonts mklink /J fonts "${REPO_PRIMARY_PATH}\WebContent\fonts"
if not exist ${MOUNT_BASE_PATH}\staticweb\HelpDocs mklink /J HelpDocs "${REPO_PRIMARY_PATH}\WebContent\HelpDocs"
if not exist ${MOUNT_BASE_PATH}\staticweb\jstemplates mklink /J jstemplates "${REPO_PRIMARY_PATH}\WebContent\jstemplates"
if not exist ${MOUNT_BASE_PATH}\staticweb\ngtemplates mklink /J ngtemplates "${REPO_PRIMARY_PATH}\WebContent\ngtemplates"
if not exist ${MOUNT_BASE_PATH}\staticweb\rflxfonts mklink /J rflxfonts "${REPO_PRIMARY_PATH}\WebContent\rflxfonts"
if not exist ${MOUNT_BASE_PATH}\staticweb\scripts mklink /J scripts "${REPO_PRIMARY_PATH}\WebContent\scripts"
if not exist ${MOUNT_BASE_PATH}\staticweb\scripts_rta mklink /J scripts_rta "${REPO_PRIMARY_PATH}\WebContent\scripts_rta"
if not exist ${MOUNT_BASE_PATH}\staticweb\static mklink /J static "${REPO_PRIMARY_PATH}\WebContent\static"
if not exist ${MOUNT_BASE_PATH}\staticweb\tpc mklink /J tpc "${REPO_PRIMARY_PATH}\WebContent\tpc"
