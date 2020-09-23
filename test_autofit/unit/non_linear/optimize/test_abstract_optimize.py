import os
import pytest

from autoconf import conf
import autofit as af

from autofit.non_linear.samples import OptimizerSamples
from test_autofit.mock import MockClassx4

directory = os.path.dirname(os.path.realpath(__file__))
pytestmark = pytest.mark.filterwarnings("ignore::FutureWarning")


@pytest.fixture(name="samples")
def make_samples():
    model = af.ModelMapper(mock_class_1=MockClassx4)

    parameters = [
        [0.0, 1.0, 2.0, 3.0],
        [0.0, 1.0, 2.0, 3.0],
        [0.0, 1.0, 2.0, 3.0],
        [21.0, 22.0, 23.0, 24.0],
        [0.0, 1.0, 2.0, 3.0],
    ]

    return OptimizerSamples(
        model=model,
        parameters=parameters,
        log_likelihoods=[1.0, 2.0, 3.0, 10.0, 5.0],
        log_priors=[0.0, 0.0, 0.0, 0.0, 0.0],
        weights=[1.0, 1.0, 1.0, 1.0, 1.0],
    )


@pytest.fixture(autouse=True)
def set_config_path():
    conf.instance = conf.Config(
        config_path=os.path.join(directory, "files/pyswarms/config"),
        output_path=os.path.join(directory, "files/pyswarms/output"),
    )


class TestJsonCSV:
    def test__from_csv_table_and_json_info(self, samples):

        optimize = af.PySwarmsGlobal()

        samples.write_table(filename=f"{optimize.paths.samples_path}/samples.csv")
        samples.info_to_json(filename=f"{optimize.paths.samples_path}/info.json")

        model = af.ModelMapper(mock_class_1=MockClassx4)

        samples = optimize.samples_via_csv_json_from_model(model=model)

        assert samples.parameters == [
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0],
            [21.0, 22.0, 23.0, 24.0],
            [0.0, 1.0, 2.0, 3.0],
        ]
        assert samples.log_likelihoods == [1.0, 2.0, 3.0, 10.0, 5.0]
        assert samples.log_priors == [0.0, 0.0, 0.0, 0.0, 0.0]
        assert samples.log_posteriors == [1.0, 2.0, 3.0, 10.0, 5.0]
        assert samples.weights == [1.0, 1.0, 1.0, 1.0, 1.0]