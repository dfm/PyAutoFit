from typing import Callable, cast
from typing import List

import numpy as np

from autofit.graphical.factor_graphs.factor import Factor
from autofit.graphical.factor_graphs.graph import FactorGraph
from autofit.graphical.mean_field import MeanFieldApproximation
from autofit.graphical.messages import NormalMessage
from autofit.mapper.prior_model.prior_model import PriorModel


class ModelFactor(Factor):
    def __init__(
            self,
            prior_model: PriorModel,
            likelihood_function: Callable
    ):
        """
        A factor in the graph that actually computes the likelihood of a model
        given values for each variable that model contains

        Parameters
        ----------
        prior_model
            A model with some dimensionality
        likelihood_function
            A function that evaluates how well an instance of the model fits some data
        """
        prior_variable_dict = {
            prior.name: prior
            for prior
            in prior_model.priors
        }

        def _factor(
                **kwargs: np.ndarray
        ) -> float:
            """
            Creates an instance of the prior model and evaluates it, forming
            a factor.

            Parameters
            ----------
            kwargs
                Arguments with names that are unique for each prior.

            Returns
            -------
            Calculated likelihood
            """
            arguments = dict()
            for name, array in kwargs.items():
                prior_id = int(name.split("_")[1])
                prior = prior_model.prior_with_id(
                    prior_id
                )
                arguments[prior] = array
            instance = prior_model.instance_for_arguments(
                arguments
            )
            return likelihood_function(instance)

        super().__init__(
            _factor,
            **prior_variable_dict
        )
        self.likelihood_function = likelihood_function
        self.prior_model = prior_model


class LikelihoodModelCollection:
    def __init__(
            self,
            likelihood_models: List["LikelihoodModel"]
    ):
        """
        A collection of likelihood models. Used to conveniently construct a mean field prior
        model with a graph of the class used to fit data.

        Parameters
        ----------
        likelihood_models
            A collection of models each of which comprises a model and a fit
        """
        self.likelihood_models = likelihood_models

    @property
    def priors(self):
        return {
            prior
            for model
            in self.likelihood_models
            for prior
            in model.prior_model.priors
        }

    @property
    def prior_factors(self):
        return [
            Factor(
                prior,
                x=prior
            )
            for prior
            in self.priors
        ]

    @property
    def message_dict(self):
        return {
            prior: NormalMessage.from_prior(
                prior
            )
            for prior
            in self.priors
        }

    @property
    def graph(self) -> FactorGraph:
        return cast(
            FactorGraph,
            np.prod(
                [
                    model.factor
                    for model
                    in self.likelihood_models
                ] + self.prior_factors
            )
        )

    def mean_field_approximation(self):
        return MeanFieldApproximation.from_kws(
            self.graph,
            self.message_dict
        )

    def __mul__(self, other: "LikelihoodModelCollection"):
        return LikelihoodModelCollection(
            other.likelihood_models + self.likelihood_models
        )


class LikelihoodModel(LikelihoodModelCollection):
    def __init__(
            self,
            prior_model,
            likelihood_function
    ):
        self.prior_model = prior_model
        self.likelihood_function = likelihood_function
        super().__init__([self])

    @property
    def factor(self):
        return ModelFactor(
            self.prior_model,
            self.likelihood_function
        )
