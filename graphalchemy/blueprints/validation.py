#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================


# ==============================================================================
#                                      MODEL
# ==============================================================================

class Validator(object):
    """ Validates each property value of the given object against its specifications.

    Example use :
    >>> ok, errors = self.validator.run(obj)
    True, {}
    """

    def __init__(self, metadata_map, logger=None):
        """ Initializes the validator with a specific metadata map.

        :param metadata_map: The metadata map to validate objects agains.
        :type metadata_map: graphalchemy.blueprints.schema.MetaData
        :param logger: An optionnal logger.
        :type logger: logging.Logger
        """
        self.metadata_map = metadata_map
        self.logger = logger


    def run(self, obj):
        """ Validates an object against its specification.

        :param obj: The object to validate.
        :type obj: graphalchemy.blueprints.schema.Model
        :returns: A boolean stating if the validation was successfull, and the
        eventual list of errors.
        :rtype: boolean, dict<string, list>
        """
        metadata = self.metadata_map.for_object(obj)
        all_errors = {}
        ok = True
        for property in metadata._properties.values():
            python_value = getattr(obj, property.name_py)
            _ok, errors = property.validate(python_value)
            if _ok:
                self._log('  Property '+str(property)+' is valid')
            else:
                all_errors[property.name_py] = errors
                ok = False
                self._log('  Property '+str(property)+' is invalid : '+" ".join(errors))
        return ok, all_errors


    def _log(self, message, level=10):
        """ Thin wrapper for logging purposes.

        :param message: The message to log.
        :type message: str
        :param level: The level of the log.
        :type level: int
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.Validator
        """
        if self.logger is not None:
            self.logger.log(level, message)
        return self
