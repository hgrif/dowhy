import numpy as np
from sklearn import linear_model

from dowhy.causal_estimator import CausalEstimate
from dowhy.causal_estimator import CausalEstimator


class LinearRegressionEstimator(CausalEstimator):
    """Compute effect of treatment using linear regression.

    The coefficient of the treatment variable in the regression model is
    computed as the causal effect. Common method but the assumptions required
    are too strong. Avoid.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.debug("Back-door variables used: %s",
                          ",".join(self._target_estimand.backdoor_variables))
        self._observed_common_causes_names = self._target_estimand.backdoor_variables
        self._observed_common_causes = self._data[self._observed_common_causes_names]
        self.logger.info("Using Linear Regression Estimator")
        self.symbolic_estimator = self.construct_symbolic_estimator(self._target_estimand)
        self.logger.info(self.symbolic_estimator)

    def _estimate_effect(self):
        treatment_2d = self._treatment.values.reshape(len(self._treatment), -1)
        features = np.concatenate((treatment_2d, self._observed_common_causes),
                                  axis=1)
        model = linear_model.LinearRegression()
        model.fit(features, self._outcome)
        coefficients = model.coef_
        self.logger.debug("Coefficients of the fitted linear model: %s",
                          ",".join(map(str, coefficients)))
        estimate = CausalEstimate(estimate=coefficients[0],
                                  target_estimand=self._target_estimand,
                                  realized_estimand_expr=self.symbolic_estimator,
                                  intercept=model.intercept_)
        return estimate

    def construct_symbolic_estimator(self, estimand):
        expr = "b: " + estimand.outcome_variable + "~"
        var_list = [estimand.treatment_variable, ] + estimand.backdoor_variables
        expr += "+".join(var_list)
        return expr
