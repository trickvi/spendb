import logging
import json
from datetime import datetime

from flask import Blueprint, render_template, redirect, request
from flask.ext.login import current_user
from flask.ext.babel import gettext as _
from werkzeug.exceptions import BadRequest
from colander import Invalid

from openspending.core import db, data_manager
from openspending.model import Account, Run
from openspending.auth import require
from openspending.lib.helpers import url_for, get_dataset
from openspending.lib.helpers import flash_success
from openspending.reference.currency import CURRENCIES
from openspending.reference.country import COUNTRIES
from openspending.reference.category import CATEGORIES
from openspending.reference.language import LANGUAGES
from openspending.validation.dataset import dataset_schema
from openspending.validation.mapping import mapping_schema
from openspending.validation.views import views_schema
from openspending.validation.common import ValidationState
from openspending.views.cache import disable_cache

log = logging.getLogger(__name__)
blueprint = Blueprint('editor', __name__)


@blueprint.route('/<dataset>/editor', methods=['GET'])
def index(dataset):
    disable_cache()
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)

    entries_count = dataset.fact_table.num_entries()
    package = data_manager.package(dataset.name)
    sources = sorted(package.sources, key=lambda s: s.meta.get('created_at'))
    has_sources = len(sources) > 0
    source = sources[0] if has_sources else None
    return render_template('editor/index.html', dataset=dataset,
                           entries_count=entries_count,
                           has_sources=has_sources, source=source)


@blueprint.route('/<dataset>/editor/team', methods=['GET'])
def team_edit(dataset, errors={}, accounts=None):
    disable_cache()
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)

    accounts = accounts or dataset.managers
    accounts = [a.as_dict() for a in accounts]
    errors = errors
    return render_template('editor/team.html', dataset=dataset,
                           accounts=accounts, errors=errors)


@blueprint.route('/<dataset>/editor/team', methods=['POST'])
def team_update(dataset):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)

    errors, accounts = {}, []
    for account_name in request.form.getlist('accounts'):
        account = Account.by_name(account_name)
        if account is None:
            errors[account_name] = _("User account cannot be found.")
        else:
            accounts.append(account)
    if current_user not in accounts:
        accounts.append(current_user)

    if not len(errors):
        dataset.managers = accounts
        dataset.updated_at = datetime.utcnow()
        db.session.commit()
        flash_success(_("The team has been updated."))
    return team_edit(dataset.name, errors=errors, accounts=accounts)

