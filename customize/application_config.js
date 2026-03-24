(() => {
  const factory = (AppConfig) => {
    AppConfig.loginSalt = 'ac73deb9ef8944e51b2d4feafc2d5713764c26911aa12fd70168cc8be2754a33';
    AppConfig.minimumPasswordLength = 8;
    return AppConfig;
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory(require('../www/common/application_config_internal.js'));
  } else if (typeof define !== 'undefined' && define !== null && define.amd !== null) {
    define(['/common/application_config_internal.js'], factory);
  }
})();
