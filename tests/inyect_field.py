from pprint import pprint

from ProfileMerger import Profile
import models


if __name__ == '__main__':
    profile_test = Profile('test')
    profile_test.scan_file('tests/test_a.profile')

    print('Pre injection')
    pprint(profile_test.fields)

    test_field = models.ProfileApplicationVisibility(
        'TESTAPP', True, True
    )
    profile_test.fields[test_field.model_id] = test_field

    print('Post Injection')
    pprint(profile_test.fields)

    profile_test.save_file(override_file_path='test_output.profile')
