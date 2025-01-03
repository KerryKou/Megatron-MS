import numpy as np
import pytest
import torch as torch
from .common_utils import  get_list_of_videos
from torchvision import io
from torchvision.datasets.samplers import DistributedSampler, RandomClipSampler, UniformClipSampler
from torchvision.datasets.video_utils import VideoClips


@pytest.mark.skipif(not io.video._av_available(), reason="this test requires av")
class TestDatasetsSamplers:
    def test_random_clip_sampler(self, tmpdir):
        video_list = get_list_of_videos(tmpdir, num_videos=3, sizes=[25, 25, 25])
        video_clips = VideoClips(video_list, 5, 5)
        sampler = RandomClipSampler(video_clips, 3)
        assert len(sampler) == 3 * 3
        indices = torch.tensor(list(iter(sampler)))
        videos = torch.div(indices, 5, rounding_mode="floor").numpy()
        v_idxs, count = np.unique(videos, return_counts=True)
        assert np.allclose(v_idxs, torch.tensor([0, 1, 2]).numpy())
        assert np.allclose(count, torch.tensor([3, 3, 3]).numpy())

    def test_random_clip_sampler_unequal(self, tmpdir):
        video_list = get_list_of_videos(tmpdir, num_videos=3, sizes=[10, 25, 25])
        video_clips = VideoClips(video_list, 5, 5)
        sampler = RandomClipSampler(video_clips, 3)
        assert len(sampler) == 2 + 3 + 3
        indices = list(iter(sampler))
        assert 0 in indices
        assert 1 in indices
        # remove elements of the first video, to simplify testing
        indices.remove(0)
        indices.remove(1)
        indices = torch.tensor(indices) - 2
        videos = torch.div(indices, 5, rounding_mode="floor").numpy()
        v_idxs, count = np.unique(videos, return_counts=True)
        assert np.allclose(v_idxs, torch.tensor([0, 1]).numpy())
        assert np.allclose(count, torch.tensor([3, 3]).numpy())

    def test_uniform_clip_sampler(self, tmpdir):
        video_list = get_list_of_videos(tmpdir, num_videos=3, sizes=[25, 25, 25])
        video_clips = VideoClips(video_list, 5, 5)
        sampler = UniformClipSampler(video_clips, 3)
        assert len(sampler) == 3 * 3
        indices = torch.tensor(list(iter(sampler)))
        videos = torch.div(indices, 5, rounding_mode="floor").numpy()
        v_idxs, count = np.unique(videos, return_counts=True)
        assert np.allclose(v_idxs, torch.tensor([0, 1, 2]).numpy())
        assert np.allclose(count, torch.tensor([3, 3, 3]).numpy())
        assert np.allclose(indices.numpy(), torch.tensor([0, 2, 4, 5, 7, 9, 10, 12, 14]).numpy())

    def test_uniform_clip_sampler_insufficient_clips(self, tmpdir):
        video_list = get_list_of_videos(tmpdir, num_videos=3, sizes=[10, 25, 25])
        video_clips = VideoClips(video_list, 5, 5)
        sampler = UniformClipSampler(video_clips, 3)
        assert len(sampler) == 3 * 3
        indices = torch.tensor(list(iter(sampler)))
        assert np.allclose(indices.numpy(), torch.tensor([0, 0, 1, 2, 4, 6, 7, 9, 11]).numpy())

    def test_distributed_sampler_and_uniform_clip_sampler(self, tmpdir):
        video_list = get_list_of_videos(tmpdir, num_videos=3, sizes=[25, 25, 25])
        video_clips = VideoClips(video_list, 5, 5)
        clip_sampler = UniformClipSampler(video_clips, 3)

        distributed_sampler_rank0 = DistributedSampler(
            clip_sampler,
            num_replicas=2,
            rank=0,
            group_size=3,
        )
        indices = torch.tensor(list(iter(distributed_sampler_rank0)))
        assert len(distributed_sampler_rank0) == 6
        assert np.allclose(indices.numpy(), torch.tensor([0, 2, 4, 10, 12, 14]).numpy())

        distributed_sampler_rank1 = DistributedSampler(
            clip_sampler,
            num_replicas=2,
            rank=1,
            group_size=3,
        )
        indices = torch.tensor(list(iter(distributed_sampler_rank1)))
        assert len(distributed_sampler_rank1) == 6
        assert np.allclose(indices.numpy(), torch.tensor([5, 7, 9, 0, 2, 4]).numpy())


if __name__ == "__main__":
    pytest.main([__file__])